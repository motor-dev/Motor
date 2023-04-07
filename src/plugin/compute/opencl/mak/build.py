from waflib import Task
from waflib.TaskGen import task_gen, feature, before_method, extension
import pickle


class embed_cl(Task.Task):
    "embed_cl"
    color = 'CYAN'

    def run(self):
        with open(self.inputs[0].abspath(), 'rb') as input_file:
            container = pickle.load(input_file)
        params = {'kernel_name': '_'.join(self.generator.kernel_name)}
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
                '_MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel32, s_%(kernel_name)scldata32);\n'
                '_MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel32Size, s_%(kernel_name)scldata32_size);\n'
                '_MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel64, s_%(kernel_name)scldata64);\n'
                '_MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel64Size, s_%(kernel_name)scldata64_size);\n'
                '\n'
                '_MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n'
                '_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32);\n'
                '_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32Size);\n'
                '_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64);\n'
                '_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64Size);' % params
            )


def create_cl_kernel(task_gen, kernel_name, kernel_source, kernel_node, kernel_type):
    if kernel_type == 'cpu':
        return

    kernel_gens = []
    kernel_target = '.'.join([task_gen.name, '.'.join(kernel_name), 'cl'])
    for env in task_gen.bld.multiarch_envs:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'opencl':
                continue
            kernel_env = task_gen.bld.all_envs[toolchain]
            tgen = task_gen.bld.get_tgen_by_name(env.ENV_PREFIX % task_gen.name)

            kernel_task_gen = task_gen.bld(
                env=kernel_env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=env.ENV_PREFIX % task_gen.name,
                safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                kernel_source=kernel_source,
                kernel_node=kernel_node,
                kernel_name=kernel_name,
                features=[
                    'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                    'motor:kernel_create', 'motor:cl:kernel_create'
                ],
                defines=tgen.defines + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                ],
                includes=tgen.includes,
                use=tgen.use + [env.ENV_PREFIX % 'plugin.compute.opencl'],
                uselib=tgen.uselib,
                source_nodes=tgen.source_nodes
            )
            kernel_task_gen.env.PLUGIN = kernel_task_gen.env.plugin_name
            kernel_gens.append(kernel_task_gen)
    task_gen.bld.multiarch(kernel_target, kernel_gens)


@feature('motor:cl:kernel_create')
@before_method('process_source')
def create_cc_source(task_gen):
    source = task_gen.kernel_node
    cc_source = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.trampoline.cc')
    task_gen.create_task('embed_cl', [source], [cc_source])
    task_gen.source += [cc_source]


@extension('.32.ll', '.64.ll')
def cl_kernel_compile(task_gen, source):
    if 'motor:cl:kernel_create' in task_gen.features:
        ptr_size = source.name[-5:-3]
        cl_source = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.generated.cl')
        cl_cc = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.embedded.cc')

        task_gen.create_task('ircc', [source], [cl_source], ircc_target=task_gen.bld.env.IRCC_CL_TARGET)
        task_gen.create_task(
            'bin2c', [cl_source], [cl_cc],
            var='%scldata%s' % ('_'.join(task_gen.kernel_name), ptr_size),
            zero_terminate=True
        )
        task_gen.source += [cl_cc]


def build(build_context):
    build_context.env.IRCC_CL_TARGET = build_context.path.find_node('ir2cl')
    task_gen.kernel_processors.append(create_cl_kernel)
