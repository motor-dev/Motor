import os
import pickle
import waflib.Task
import waflib.Errors
import waflib.TaskGen
import waflib.Build
import waflib.Node
import build_framework
import kernel_support
from typing import List, Tuple


class cpuc(waflib.Task.Task):
    """Generates a C++ trampoline to call the CPU kernel"""
    color = 'CYAN'

    # noinspection PyMethodMayBeStatic
    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:
        return [], []

    def run(self) -> None:
        kernel_node = getattr(self.generator, 'kernel_node')  # type: waflib.Node.Node
        variant_name = getattr(self.generator, 'variant_name')  # type: str
        with open(kernel_node.abspath(), 'rb') as kernel_file:
            namespace = pickle.load(kernel_file)  # type: kernel_support.KernelNamespace
        static_variant = ('_' + variant_name.replace('.', '_')) if self.env.STATIC else ''

        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(
                '#include <motor/config/config.hh>\n'
                '#include <motor/kernel/input/input.hh>\n'
                '#include <motor/kernel/simd.hh>\n'
                '#include <motor/minitl/vector.hh>\n'
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
                'MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);\n' % getattr(self.generator,
                                                                                         'kernel_source')
            )

            def write_kernels(ns: List[str], container: kernel_support.KernelNamespace) -> None:
                for namespace_name, c in container.children.items():
                    write_kernels(ns + [namespace_name], c)
                for method, kernel in container.kernels.items():
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
                                    for i, (arg, index) in enumerate(kernel.parameters[2:])
                                ]
                            ),
                        'arguments':
                            ', '.join(['arg_type_%d(0, 0, 0)' % i for i, _ in enumerate(kernel.parameters[2:])])
                    }
                    out.write(
                        'MOTOR_PLUGIN_EXPORT void _%(kernelname)s%(static_variant)s(const u32 index, const u32 total,\n'
                        '        const minitl::vector<\n'
                        '        minitl::weak< const Motor::KernelScheduler::IMemoryBuffer > >& /*argv*/)\n'
                        '{\n'
                        '    %(namespace)s\n'
                        '    %(typedef)s'
                        '    %(kernelname)s(index, total, %(arguments)s);\n'
                        '}\n'
                        'MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _'
                        '%(kernelname)s%(static_variant)s, _%(kernelname)s);\n'
                        % args
                    )

            write_kernels([], namespace)


@waflib.TaskGen.feature('motor:cpu:kernel_create')
def build_cpu_kernels(task_gen: waflib.TaskGen.task_gen) -> None:
    out = build_framework.make_bld_node(task_gen,
                                        'src/kernels', None,
                                        '%s.cc' % os.path.join(*getattr(task_gen, 'kernel_name'))
                                        )
    task_gen.create_task('cpuc', [getattr(task_gen, 'kernel_node')], [out])
    task_gen.source.append(out)


def create_cpu_kernel(
        build_context: build_framework.BuildContext,
        task_gen: waflib.TaskGen.task_gen,
        kernel_name: List[str],
        kernel_source: waflib.Node.Node,
        kernel_node: waflib.Node.Node,
        kernel_type: str
) -> None:
    env = task_gen.env
    target_name = getattr(task_gen, 'target_name')  # type: str

    if not env.PROJECTS:
        for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
            if kernel_type != 'cpu':
                continue
            kernel_env = build_context.all_envs[toolchain]
            for variant in kernel_env.VECTOR_OPTIM_VARIANTS:
                tgen = build_context.get_tgen_by_name(task_gen.name)
                target_suffix = env.ARCH_NAME + variant
                kernel_target = target_name + '.' + '.'.join(kernel_name) + '.' + target_suffix
                kernel_task_gen = build_context(
                    group=build_context.motor_variant,
                    env=kernel_env.derive(),
                    bld_env=env,
                    target=env.ENV_PREFIX % kernel_target,
                    target_name=task_gen.name,
                    variant_name=env.ARCH_NAME + variant,
                    kernel_source=kernel_source,
                    kernel_name=kernel_name,
                    kernel_node=kernel_node,
                    features=[
                        'cxx', build_context.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                        'motor:cpu:kernel_create'
                    ],
                    defines=getattr(tgen, 'defines') + [
                        'MOTOR_KERNEL_ID=%s_%s' % (
                            target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                        'MOTOR_KERNEL_NAME=%s' % kernel_target,
                        'MOTOR_KERNEL_TARGET=%s' % kernel_type + '.' + env.ARCH_NAME + variant,
                    ],
                    includes=getattr(tgen, 'includes') + [build_context.srcnode],
                    use=getattr(tgen, 'use') + [env.ENV_PREFIX % 'plugin.compute.cpu'] + ([variant] if variant else []),
                    uselib=getattr(tgen, 'uselib'),
                    nomaster=set(),
                )
                kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name
                if task_gen.name != target_name:
                    try:
                        multiarch = build_context.get_tgen_by_name(kernel_target)
                    except waflib.Errors.WafError:
                        build_framework.multiarch(build_context, kernel_target, [kernel_task_gen])
                    else:
                        getattr(multiarch, 'use').append(kernel_task_gen.target)
    else:
        tgen = build_context.get_tgen_by_name(task_gen.name)
        env = task_gen.env
        kernel_target = target_name + '.' + '.'.join(kernel_name) + '.cpu'
        build_context(
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
                'MOTOR_KERNEL_ID=%s_%s' % (target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                'MOTOR_KERNEL_NAME=%s' % kernel_target,
                'MOTOR_KERNEL_TARGET=%s' % kernel_type
            ],
            includes=getattr(tgen, 'includes') + [build_context.srcnode],
            use=[tgen.target] + getattr(tgen, 'use') + [env.ENV_PREFIX % 'plugin.compute.cpu'],
            uselib=getattr(tgen, 'uselib'),
            source_nodes=[('', kernel_source)],
            nomaster=set(),
        )


def build(build_context: build_framework.BuildContext) -> None:
    build_context.kernel_processors.append(create_cpu_kernel)
