import pickle
import build_framework
import kernel_support
import waflib.Errors
import waflib.Node
import waflib.Task
import waflib.TaskGen
from typing import List


class embed_cl(waflib.Task.Task):
    color = 'CYAN'

    def run(self) -> None:
        with open(self.inputs[0].abspath(), 'rb') as input_file:
            container = pickle.load(input_file)  # type: kernel_support.KernelNamespace
        params = {'kernel_name': '_'.join(getattr(self.generator, 'kernel_name'))}
        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(
                '#include    <motor/config/config.hh>\n'
                '#include    <motor/kernel/simd.hh>\n'
                '#include    <motor/kernel/input/input.hh>\n'
                '#include    <motor/plugin/dynobjectlist.hh>\n'
                '\n'
                'extern const unsigned char s_%(kernel_name)scldata32[];\n'
                'extern const unsigned long s_%(kernel_name)scldata32_size;\n'
                'extern const unsigned char s_%(kernel_name)scldata64[];\n'
                'extern const unsigned long s_%(kernel_name)scldata64_size;\n'
                '\n'
                'MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel32, s_%(kernel_name)scldata32);\n'
                'MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel32Size, s_%(kernel_name)scldata32_size);\n'
                'MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel64, s_%(kernel_name)scldata64);\n'
                'MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel64Size, s_%(kernel_name)scldata64_size);\n'
                '\n'
                'MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n'
                'MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32);\n'
                'MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32Size);\n'
                'MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64);\n'
                'MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64Size);' % params
            )


def create_cl_kernel(
        build_context: build_framework.BuildContext,
        task_gen: waflib.TaskGen.task_gen,
        kernel_name: List[str],
        kernel_source: waflib.Node.Node,
        kernel_node: waflib.Node.Node,
        kernel_type: str
) -> None:
    if kernel_type == 'cpu':
        return

    kernel_target = '.'.join([task_gen.name, '.'.join(kernel_name), 'cl'])
    env = task_gen.env

    if not env.PROJECTS:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'opencl':
                continue
            kernel_env = build_context.all_envs[toolchain]

            kernel_task_gen = build_context(
                env=kernel_env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=env.ENV_PREFIX % task_gen.name,
                kernel_source=kernel_source,
                kernel_node=kernel_node,
                kernel_name=kernel_name,
                features=[
                    'cxx', build_context.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                    'motor:kernel_create', 'motor:cl:kernel_create'
                ],
                defines=getattr(task_gen, 'defines') + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % kernel_target,
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                ],
                includes=getattr(task_gen, 'includes'),
                use=getattr(task_gen, 'use') + [env.ENV_PREFIX % 'plugin.compute.opencl'],
                uselib=getattr(task_gen, 'uselib'),
                source_nodes=getattr(task_gen, 'source_nodes'),
                nomaster=set()
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

        target_name = getattr(task_gen, 'target_name')
        kernel_target = target_name + '.' + '.'.join(kernel_name) + '.cl'
        kernel_task_gen = build_context(
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
                'MOTOR_KERNEL_ID=%s_%s' % (target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                'MOTOR_KERNEL_NAME=%s' % kernel_target,
                'MOTOR_KERNEL_TARGET=%s' % kernel_type
            ],
            includes=getattr(tgen, 'includes') + [build_context.srcnode] + env.CLC_KERNEL_HEADER_PATH,
            use=[tgen.target] + getattr(tgen, 'use') + [env.ENV_PREFIX % 'plugin.compute.cl'],
            uselib=getattr(tgen, 'uselib'),
            source_nodes=[('', kernel_source)],
            nomaster=set()
        )
        kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name


@waflib.TaskGen.feature('motor:cl:kernel_create')
@waflib.TaskGen.before_method('process_source')
def create_cc_source(task_gen: waflib.TaskGen.task_gen) -> None:
    source = getattr(task_gen, 'kernel_node')  # type: waflib.Node.Node
    cc_source = build_framework.make_bld_node(task_gen, 'src', source.parent,
                                              source.name[:source.name.rfind('.')] + '.trampoline.cc')
    task_gen.create_task('embed_cl', [source], [cc_source])
    task_gen.source += [cc_source]


@waflib.TaskGen.extension('.32.ll', '.64.ll')
def cl_kernel_compile(task_gen: waflib.TaskGen.task_gen, source: waflib.Node.Node) -> None:
    if 'motor:cl:kernel_create' in task_gen.features:
        ptr_size = source.name[-5:-3]
        cl_source = build_framework.make_bld_node(task_gen, 'src', source.parent,
                                                  source.name[:source.name.rfind('.')] + '.generated.cl')
        cl_cc = build_framework.make_bld_node(task_gen, 'src', source.parent,
                                              source.name[:source.name.rfind('.')] + '.embedded.cc')

        task_gen.create_task('ircc', [source], [cl_source], ircc_target=task_gen.bld.env.IRCC_CL_TARGET)
        task_gen.create_task(
            'bin2c', [cl_source], [cl_cc],
            var='%scldata%s' % ('_'.join(getattr(task_gen, 'kernel_name')), ptr_size),
            zero_terminate=True
        )
        task_gen.source += [cl_cc]


def build(build_context: build_framework.BuildContext) -> None:
    build_context.env.IRCC_CL_TARGET = build_context.path.find_node('ir2cl')
    build_context.kernel_processors.append(create_cl_kernel)
    if build_context.env.PROJECTS:
        build_context.env.CLC_KERNEL_HEADER_PATH = [build_context.path.parent.make_node('api.cl').abspath()]
