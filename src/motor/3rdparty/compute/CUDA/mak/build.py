from waflib import Task, Errors
from waflib.TaskGen import task_gen, feature, before_method
from waflib.Tools import c_preproc, ccroot
import pickle

template_kernel = """
_MOTOR_PLUGIN_EXPORT void _%(kernel)s(const u32 index, const u32 total,
                              const minitl::array< minitl::weak<const Motor::KernelScheduler::IMemoryBuffer> >& /*argv*/)
{
    motor_forceuse(index);
    motor_forceuse(total);
}
_MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernel)s, _%(kernel)s);
"""

template_cpp = """
#include    <motor/config/config.hh>
#include    <motor/kernel/simd.hh>
#include    <motor/kernel/input/input.hh>
#include    <motor/plugin/dynobjectlist.hh>
#include    <motor/minitl/array.hh>
#include    <motor/plugin.compute.cuda/memorybuffer.hh>
#include    <motor/scheduler/kernel/parameters/parameters.hh>

using namespace knl;

_MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);

%(kernels)s

"""

ccroot.USELIB_VARS['cxx'].add('NVCC_CXXFLAGS')


class nvcc(Task.Task):
    "nvcc"
    run_str = '${NVCC_CXX} ${NVCC_CXXFLAGS} --fatbin ${NVCC_FRAMEWORKPATH_ST:FRAMEWORKPATH} ${NVCC_CPPPATH_ST:INCPATHS} -DMOTOR_COMPUTE=2 ${NVCC_DEFINES_ST:DEFINES} -D_NVCC=1 ${NVCC_CXX_SRC_F}${SRC[0].abspath()} ${NVCC_CXX_TGT_F} ${TGT}'
    ext_out = ['.fatbin']

    def scan(self):
        try:
            incn = self.generator.includes_nodes
        except AttributeError:
            raise Errors.WafError('%r is missing a feature such as "c", "cxx" or "includes": ' % self.generator)

        nodepaths = [x for x in incn if x.is_child_of(x.ctx.srcnode) or x.is_child_of(x.ctx.bldnode)]
        nodepaths.append(self.generator.bld.motornode.make_node('src/plugin/compute/cuda/api.cuda'))

        tmp = c_preproc.c_parser(nodepaths)
        tmp.start(self.inputs[0], self.env)
        return (tmp.nodes, tmp.names)

    color = 'GREEN'


class cudac(Task.Task):
    "Generates a CUDA binder to call the C++ kernel"
    color = 'CYAN'

    def sig_vars(self):
        Task.Task.sig_vars(self)
        self.m.update(template_kernel.encode('utf-8'))
        self.m.update(template_cpp.encode('utf-8'))

    def scan(self):
        return ([], [])

    def run(self):
        with open(self.generator.kernel_node.abspath(), 'rb') as kernel_file:
            namespace = pickle.load(kernel_file)

        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(
                '#include <motor/config/config.hh>\n'
                '#include <motor/kernel/input/input.hh>\n'
                '#include <motor/kernel/simd.hh>\n'
                '#include <motor/minitl/array.hh>\n'
                '#include <motor/plugin.compute.cuda/memorybuffer.hh>\n'
                '#include <motor/plugin/dynobjectlist.hh>\n'
                '#include <motor/scheduler/kernel/parameters/parameters.hh>\n'
                '\n'
                'using namespace knl;\n'
                '\n'
                '_MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n'
            )

            def write_kernels(ns, container):
                for namespace_name, c in container[2].items():
                    write_kernels(ns + [namespace_name], c)
                for method, arguments in container[3].items():
                    args = {
                        'kernelname':
                            method,
                        'namespace': ('using namespace %s;' % '::'.join(ns)) if ns else '',
                        'typedef':
                            '\n    '.join(
                                [
                                    'typedef %sarg_type_%d%s;' % (arg[:index[0]], i, arg[index[1]:])
                                    for i, (arg, index) in enumerate(arguments[2:])
                                ]
                            ),
                        'arguments':
                            ', '.join(['arg_type_%d(0, 0, 0)' % i for i, _ in enumerate(arguments[2:])])
                    }
                    out.write(
                        '_MOTOR_PLUGIN_EXPORT void _%(kernelname)s(const u32 index, const u32 total,\n'
                        '        const minitl::array<\n'
                        '        minitl::weak< const Motor::KernelScheduler::IMemoryBuffer > >& /*argv*/)\n'
                        '{\n'
                        '    motor_forceuse(index);\n'
                        '    motor_forceuse(total);\n'
                        '}\n'
                        '_MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernelname)s, _%(kernelname)s);\n' % args
                    )

            write_kernels([], namespace)


@feature('motor:cuda:kernel_create')
@before_method('process_source')
def build_cuda_kernels(task_gen):
    for f in getattr(task_gen, 'features', []):
        task_gen.env.append_value('NVCC_CXXFLAGS', task_gen.env['NVCC_CXXFLAGS_%s' % f])
    kernel_node = task_gen.kernel_node
    cuda_source = task_gen.kernel_source
    out_cc = kernel_node.change_ext('.cudacall.cc')
    task_gen.create_task('cudac', [kernel_node], [out_cc])
    task_gen.source.append(out_cc)
    cuda_bin = task_gen.make_bld_node('obj', cuda_source.parent, cuda_source.name[:-2] + 'fatbin')
    cuda_cc = task_gen.make_bld_node('src', cuda_source.parent, cuda_source.name[:-2] + 'cc')
    task_gen.create_task('nvcc', [cuda_source], [cuda_bin])
    task_gen.create_task('bin2c', [cuda_bin], [cuda_cc], var='%s_cudaKernel' % '_'.join(task_gen.kernel_name))
    task_gen.source.append(cuda_cc)


def create_cuda_kernel(task_gen, kernel_name, kernel_source, kernel_node, kernel_type):
    if kernel_type == 'cpu':
        return
    kernel_target = '.'.join([task_gen.name, '.'.join(kernel_name), 'cuda'])
    kernel_gens = []
    for env in task_gen.bld.multiarch_envs:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'cuda':
                continue
            kernel_env = task_gen.bld.all_envs[toolchain]
            tgen = task_gen.bld.get_tgen_by_name(env.ENV_PREFIX % task_gen.name)

            kernel_task_gen = task_gen.bld(
                env=kernel_env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=env.ENV_PREFIX % task_gen.name,
                safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                kernel_name=kernel_name,
                kernel_source=kernel_source,
                kernel_node=kernel_node,
                features=[
                    'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                    'motor:cuda:kernel_create'
                ],
                defines=tgen.defines + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                ],
                includes=tgen.includes,
                use=tgen.use + [env.ENV_PREFIX % 'plugin.compute.cuda'],
                uselib=tgen.uselib,
                source_nodes=tgen.source_nodes,
            )
            kernel_task_gen.env.PLUGIN = kernel_task_gen.env.plugin_name
            kernel_gens.append(kernel_task_gen)
    task_gen.bld.multiarch(kernel_target, kernel_gens)


def build(bld):
    cuda = bld.thirdparty('motor.3rdparty.compute.CUDA')
    if cuda:
        task_gen.kernel_processors.append(create_cuda_kernel)
