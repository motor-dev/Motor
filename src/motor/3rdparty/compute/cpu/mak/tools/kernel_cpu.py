from waflib import Task, Errors
from waflib.TaskGen import feature, task_gen, before_method

import os
import pickle


class cpuc(Task.Task):
    "Generates a C++ trampoline to call the CPU kernel"
    color = 'CYAN'

    def scan(self):
        return ([], [])

    def run(self):
        with open(self.generator.kernel_node.abspath(), 'rb') as kernel_file:
            namespace = pickle.load(kernel_file)
        static_variant = ('_' + self.generator.variant_name[1:]) if self.env.STATIC else ''

        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(
                '#include <motor/config/config.hh>\n'
                '#include <motor/kernel/input/input.hh>\n'
                '#include <motor/kernel/simd.hh>\n'
                '#include <motor/minitl/array.hh>\n'
                '#include <motor/plugin.compute.cpu/memorybuffer.hh>\n'
                '#include <motor/plugin/dynobjectlist.hh>\n'
                '#include <motor/scheduler/kernel/parameters/parameters.hh>\n'
                '\n'
                'using namespace knl;\n'
                '\n'
                '#include "%s"\n'
                '\n'
                'struct Parameter\n'
                '{\n'
                '    void* begin;\n'
                '    void* end;\n'
                '};\n'
                '\n'
                'MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n' % self.generator.kernel_source
            )

            def write_kernels(ns, container):
                for namespace_name, c in container[2].items():
                    write_kernels(ns + [namespace_name], c)
                for method, arguments in container[3].items():
                    args = {
                        'kernelname':
                            method,
                        'static_variant':
                            static_variant,
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
                        'MOTOR_PLUGIN_EXPORT void _%(kernelname)s%(static_variant)s(const u32 index, const u32 total,\n'
                        '        const minitl::array<\n'
                        '        minitl::weak< const Motor::KernelScheduler::IMemoryBuffer > >& /*argv*/)\n'
                        '{\n'
                        '    %(namespace)s\n'
                        '    %(typedef)s'
                        '    %(kernelname)s(index, total, %(arguments)s);\n'
                        '}\n'
                        'MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernelname)s%(static_variant)s, _%(kernelname)s);\n'
                        % args
                    )

            write_kernels([], namespace)


class cpu_header(Task.Task):
    color = 'BLUE'
    ext_out = ['.h']

    def scan(self):
        return ([], [])

    vars = ['VECTOR_OPTIM_VARIANTS']

    def run(self):
        self.outputs[0].write(
            "static const char* s_cpuVariants[] = { %s };\n"
            "static const i32 s_cpuVariantCount = %d;\n"
            "" % (
                ', '.join('"%s"' % o for o in [''] + [v[1:] for v in self.env.VECTOR_OPTIM_VARIANTS]
                          ), 1 + len(self.env.VECTOR_OPTIM_VARIANTS)
            )
        )


@feature('motor:cpu:variants')
@before_method('process_source')
def generate_cpu_variant_header(self):
    for kernel_name, toolchain in self.env.KERNEL_TOOLCHAINS:
        if kernel_name == 'cpu':
            env = self.bld.all_envs[toolchain]
            out_header = self.make_bld_node('include', None, 'kernel_optims.hh')
            task = self.create_task('cpu_header', [], [out_header])
            self.includes.append(out_header.parent)


@feature('motor:cpu:kernel_create')
def build_cpu_kernels(task_gen):
    out = task_gen.make_bld_node(
        'src/kernels', None, '%s.cpu%s.cc' % (os.path.join(*task_gen.kernel_name), task_gen.variant_name)
    )
    task_gen.create_task('cpuc', [task_gen.kernel_node], [out])
    task_gen.source.append(out)


def create_cpu_kernel(task_gen, kernel_name, kernel_source, kernel_node, kernel_type):
    env = task_gen.env
    for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
        if kernel_type != 'cpu':
            continue
        kernel_env = task_gen.bld.all_envs[toolchain]
        for variant in kernel_env.VECTOR_OPTIM_VARIANTS:
            tgen = task_gen.bld.get_tgen_by_name(task_gen.name)
            target_suffix = '.'.join([kernel_type] + ([variant[1:]] if variant else []))
            kernel_target = task_gen.target_name + '.' + '.'.join(kernel_name) + '.' + target_suffix
            kernel_task_gen = task_gen.bld(
                env=kernel_env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=task_gen.name,
                safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                variant_name=variant,
                kernel_source=kernel_source,
                kernel_name=kernel_name,
                kernel_node=kernel_node,
                features=[
                    'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                    'motor:cpu:kernel_create'
                ],
                defines=tgen.defines + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                    'MOTOR_KERNEL_ARCH=%s' % variant
                ],
                includes=tgen.includes + [task_gen.bld.srcnode],
                use=tgen.use + [env.ENV_PREFIX % 'plugin.compute.cpu'] + ([variant] if variant else []),
                uselib=tgen.uselib,
            )
            kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name
            if task_gen.name != task_gen.target_name:
                try:
                    multiarch = task_gen.bld.get_tgen_by_name(kernel_target)
                except Errors.WafError:
                    task_gen.bld.multiarch(kernel_target, [kernel_task_gen])
                else:
                    multiarch.use.append(kernel_task_gen.target)


def build(build_context):
    task_gen.kernel_processors.append(create_cpu_kernel)