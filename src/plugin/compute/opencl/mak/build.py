from waflib import Task, Errors
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


def create_cl_kernel(task_gen, kernel_name, kernel_source, kernel_node, kernel_type):
    if kernel_type == 'cpu':
        return

    kernel_target = '.'.join([task_gen.name, '.'.join(kernel_name), 'cl'])
    env = task_gen.env

    if not env.PROJECTS:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'opencl':
                continue
            kernel_env = task_gen.bld.all_envs[toolchain]

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
                defines=task_gen.defines + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % kernel_target,
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                ],
                includes=task_gen.includes,
                use=task_gen.use + [env.ENV_PREFIX % 'plugin.compute.opencl'],
                uselib=task_gen.uselib,
                source_nodes=task_gen.source_nodes,
                nomaster=set()
            )
            kernel_task_gen.env.PLUGIN = kernel_task_gen.env.plugin_name

            if task_gen.name != task_gen.target_name:
                try:
                    multiarch = task_gen.bld.get_tgen_by_name(kernel_target)
                except Errors.WafError:
                    task_gen.bld.multiarch(kernel_target, [kernel_task_gen])
                else:
                    multiarch.use.append(kernel_task_gen.target)
    else:
        tgen = task_gen.bld.get_tgen_by_name(task_gen.name)
        target_suffix = '.'.join([kernel_type])

        kernel_target = task_gen.target_name + '.' + '.'.join(kernel_name) + '.cl'
        kernel_task_gen = task_gen.bld(
            env=task_gen.env.derive(),
            bld_env=env,
            target=env.ENV_PREFIX % kernel_target,
            target_name=task_gen.name,
            safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
            source=[kernel_source],
            kernel_name=kernel_name,
            kernel_node=kernel_node,
            features=[
                'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel'
            ],
            defines=tgen.defines + [
                'MOTOR_KERNEL_ID=%s_%s' % (task_gen.target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                'MOTOR_KERNEL_TARGET=%s' % kernel_type
            ],
            includes=tgen.includes + [task_gen.bld.srcnode] + env.CLC_KERNEL_HEADER_PATH,
            use=[tgen.target] + tgen.use + [env.ENV_PREFIX % 'plugin.compute.cl'],
            uselib=tgen.uselib,
            source_nodes=[('', kernel_source)],
            nomaster=set()
        )
        kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name


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
    if build_context.env.PROJECTS:
        build_context.env.CLC_KERNEL_HEADER_PATH = [build_context.path.parent.make_node('api.cl').abspath()]
