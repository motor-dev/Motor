import pickle

import kernel_support
import waflib.Task
import waflib.TaskGen
import waflib.Errors
import waflib.Configure
import waflib.Node
import waflib.Tools.ccroot
import waflib.Tools.c_preproc
import build_framework
from typing import List, Tuple

template_kernel = """
MOTOR_PLUGIN_EXPORT void _%(kernel)s(const u32 index, const u32 total,
                              const minitl::vector< minitl::weak<const Motor::KernelScheduler::IMemoryBuffer> >& /*argv*/)
{
    motor_forceuse(index);
    motor_forceuse(total);
}
MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernel)s, _%(kernel)s);
"""

template_cpp = """
#include    <motor/config/config.hh>
#include    <motor/kernel/simd.hh>
#include    <motor/kernel/input/input.hh>
#include    <motor/plugin/dynobjectlist.hh>
#include    <motor/minitl/vector.hh>
#include    <motor/plugin.compute.cuda/memorybuffer.hh>
#include    <motor/scheduler/kernel/parameters/parameters.hh>

using namespace knl;

MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);

%(kernels)s

"""

waflib.Tools.ccroot.USELIB_VARS['cxx'].add('NVCC_CXXFLAGS')


class nvcc(waflib.Task.Task):
    """nvcc"""
    run_str = '${NVCC_CXX} ${NVCC_CXXFLAGS} --fatbin ${NVCC_FRAMEWORKPATH_ST:FRAMEWORKPATH} ' \
              '${NVCC_CPPPATH_ST:CUDA_KERNEL_HEADER_PATH} ${NVCC_CPPPATH_ST:INCPATHS} ' \
              '-DMOTOR_COMPUTE=2 ${NVCC_DEFINES_ST:DEFINES} -D_NVCC=1 ' \
              '${NVCC_CXX_SRC_F}${SRC[0].abspath()} ${NVCC_CXX_TGT_F} ${TGT}'
    ext_out = ['.fatbin']

    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:
        assert isinstance(self.generator.bld, build_framework.BuildContext)
        try:
            incn = getattr(self.generator, 'includes_nodes')
        except AttributeError:
            raise waflib.Errors.WafError('%r is missing a feature such as "c", "cxx" or "includes": ' % self.generator)

        nodepaths = [x for x in incn if x.is_child_of(x.ctx.srcnode) or x.is_child_of(x.ctx.bldnode)]
        nodepaths.extend(self.env.CUDA_KERNEL_HEADER_PATH)

        tmp = waflib.Tools.c_preproc.c_parser(nodepaths)
        tmp.start(self.inputs[0], self.env)
        return tmp.nodes, tmp.names

    color = 'GREEN'


class cudac(waflib.Task.Task):
    """Generates a CUDA binder to call the C++ kernel"""
    color = 'CYAN'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        self.m.update(template_kernel.encode('utf-8'))
        self.m.update(template_cpp.encode('utf-8'))

    # noinspection PyMethodMayBeStatic
    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:
        return [], []

    def run(self) -> None:
        kernel_node = getattr(self.generator, 'kernel_node')  # type: waflib.Node.Node
        with open(kernel_node.abspath(), 'rb') as kernel_file:
            namespace = pickle.load(kernel_file)  # type: kernel_support.KernelNamespace

        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(
                '#include <motor/config/config.hh>\n'
                '#include <motor/kernel/input/input.hh>\n'
                '#include <motor/kernel/simd.hh>\n'
                '#include <motor/minitl/vector.hh>\n'
                '#include <motor/plugin.compute.cuda/memorybuffer.hh>\n'
                '#include <motor/plugin/dynobjectlist.hh>\n'
                '#include <motor/scheduler/kernel/parameters/parameters.hh>\n'
                '\n'
                'using namespace knl;\n'
                '\n'
                'MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n'
            )

            def write_kernels(ns: List[str], container: kernel_support.KernelNamespace) -> None:
                for namespace_name, c in container.children.items():
                    write_kernels(ns + [namespace_name], c)
                for method, kernel in container.kernels.items():
                    args = {
                        'kernelname':
                            method,
                        'namespace': ('using namespace %s;' % '::'.join(ns)) if ns else '',
                        'typedef':
                            '\n    '.join(
                                [
                                    'typedef %sarg_type_%d%s;' % (arg[:index[0]], i, arg[index[1]:])
                                    for i, (arg, index) in enumerate(kernel.parameters[2:])
                                ]
                            ),
                        'arguments':
                            ', '.join(['arg_type_%d(0, 0, 0)' % i for i, _ in enumerate(kernel.parameters[2:])])
                    }
                    out.write(
                        'MOTOR_PLUGIN_EXPORT void _%(kernelname)s(const u32 index, const u32 total,\n'
                        '        const minitl::vector<\n'
                        '        minitl::weak< const Motor::KernelScheduler::IMemoryBuffer > >& /*argv*/)\n'
                        '{\n'
                        '    motor_forceuse(index);\n'
                        '    motor_forceuse(total);\n'
                        '}\n'
                        'MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernelname)s, _%(kernelname)s);\n' % args
                    )

            write_kernels([], namespace)


@waflib.TaskGen.feature('motor:cuda:kernel_create')
@waflib.TaskGen.before_method('process_source')
def build_cuda_kernels(task_gen: waflib.TaskGen.task_gen) -> None:
    for f in getattr(task_gen, 'features', []):
        task_gen.env.append_value('NVCC_CXXFLAGS', task_gen.env['NVCC_CXXFLAGS_%s' % f])
    kernel_node = getattr(task_gen, 'kernel_node')  # type: waflib.Node.Node
    cuda_source = getattr(task_gen, 'kernel_source')  # type: waflib.Node.Node
    kernel_name = getattr(task_gen, 'kernel_name')  # type: str
    out_cc = build_framework.make_bld_node(task_gen, 'src/kernels', '/'.join(kernel_name),
                                           kernel_node.name + '.cuda.cc')
    task_gen.create_task('cudac', [kernel_node], [out_cc])
    task_gen.source.append(out_cc)
    cuda_bin = build_framework.make_bld_node(task_gen, 'obj', cuda_source.parent, cuda_source.name[:-2] + 'fatbin')
    cuda_cc = build_framework.make_bld_node(task_gen, 'src', cuda_source.parent, cuda_source.name[:-2] + 'cc')
    task_gen.create_task('nvcc', [cuda_source], [cuda_bin])
    task_gen.create_task('bin2c', [cuda_bin], [cuda_cc], var='%s_cudaKernel' % '_'.join(kernel_name))
    task_gen.source.append(cuda_cc)


def create_cuda_kernel(
        build_context: build_framework.BuildContext,
        task_gen: waflib.TaskGen.task_gen,
        kernel_name: List[str],
        kernel_source: waflib.Node.Node,
        kernel_node: waflib.Node.Node,
        kernel_type: str
) -> None:
    if kernel_type == 'cpu':
        return
    env = task_gen.env
    kernel_target = '.'.join([task_gen.name, '.'.join(kernel_name), 'cuda'])
    if not env.PROJECTS:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'cuda':
                continue
            kernel_env = build_context.all_envs[toolchain]

            kernel_task_gen = build_context(
                group=build_context.motor_variant,
                env=kernel_env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=env.ENV_PREFIX % task_gen.name,
                kernel_name=kernel_name,
                kernel_source=kernel_source,
                kernel_node=kernel_node,
                features=[
                    'cxx', build_context.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                    'motor:cuda:kernel_create'
                ],
                defines=getattr(task_gen, 'defines', []) + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % kernel_target,
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                ],
                includes=getattr(task_gen, 'includes', []),
                use=getattr(task_gen, 'use', []) + [env.ENV_PREFIX % 'plugin.compute.cuda'],
                uselib=getattr(task_gen, 'uselib', []),
                source_nodes=getattr(task_gen, 'source_nodes', []),
                masterfiles={}
            )
            kernel_task_gen.env.PLUGIN = kernel_task_gen.env.plugin_name

            if task_gen.name != getattr(task_gen, 'target_name'):
                try:
                    multiarch = build_context.get_tgen_by_name(kernel_target)
                except waflib.Errors.WafError:
                    build_framework.multiarch(build_context, kernel_target, [kernel_task_gen])
                else:
                    getattr(multiarch, 'use').append(kernel_task_gen.target)
    else:
        tgen = build_context.get_tgen_by_name(task_gen.name)

        kernel_target = getattr(task_gen, 'target_name') + '.' + '.'.join(kernel_name) + '.cuda'
        project_name = getattr(tgen, 'project_name')  # type: str
        project_name += '.' + '.'.join(kernel_name) + '.cuda'
        kernel_task_gen = build_context(
            group=build_context.motor_variant,
            env=task_gen.env.derive(),
            bld_env=env,
            target=env.ENV_PREFIX % kernel_target,
            target_name=task_gen.name,
            source=[kernel_source],
            kernel_name=kernel_name,
            kernel_node=kernel_node,
            features=[
                'cxx', build_context.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel'
            ],
            defines=getattr(tgen, 'defines') + [
                'MOTOR_KERNEL_ID=%s_%s' % (
                    getattr(task_gen, 'target_name').replace('.', '_'), kernel_target.replace('.', '_')),
                'MOTOR_KERNEL_NAME=%s' % kernel_target,
                'MOTOR_KERNEL_TARGET=%s' % kernel_type
            ],
            includes=[build_context.root.make_node(i) for i in
                      build_context.env.CUDA_KERNEL_HEADER_PATH] + getattr(tgen, 'includes'),
            use=[tgen.target] + getattr(tgen, 'use') + [env.ENV_PREFIX % 'plugin.compute.cuda'],
            uselib=getattr(tgen, 'uselib'),
            source_nodes=[('', kernel_source)],
            project_name=project_name,
            masterfiles={}
        )
        kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name


def build(build_context: build_framework.BuildContext) -> None:
    if build_context.env.check_CUDA:
        build_context.kernel_processors.append(create_cuda_kernel)
