from waflib import Task, Errors
from waflib.TaskGen import feature, extension, before_method
import os
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle

template_kernel = """
_MOTOR_PLUGIN_EXPORT void _%(kernelname)s%(static_variant)s(const u32 index, const u32 total,
        const minitl::array<
           minitl::weak< const Motor::KernelScheduler::IMemoryBuffer > >& /*argv*/)
{
    %(kernelnamespace)s
    %(kernelname)s(index, total, %(args)s);
}
_MOTOR_REGISTER_METHOD_NAMED(MOTOR_KERNEL_ID, _%(kernelname)s%(static_variant)s, _%(kernelname)s);
"""

template = """
%(pch)s

#include <motor/config/config.hh>
#include <motor/kernel/input/input.hh>
#include <motor/kernel/simd.hh>
#include <motor/minitl/array.hh>
#include <motor/plugin.compute.cpu/memorybuffer.hh>
#include <motor/plugin/dynobjectlist.hh>
#include <motor/scheduler/kernel/parameters/parameters.hh>

using namespace Kernel;

#include "%(source)s"

struct Parameter
{
    void* begin;
    void* end;
};

_MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);

%(kernels)s
"""


class cpuc(Task.Task):
    "Generates a C++ trampoline to call the CPU kernel"
    color = 'CYAN'

    def sig_vars(self):
        self.m.update(template.encode('utf-8'))
        self.m.update(template_kernel.encode('utf-8'))

    def scan(self):
        return ([], [])

    def run(self):
        with open(self.inputs[0].abspath(), 'rb') as input_file:
            kernel_name, includes, source, kernel_methods = pickle.load(input_file)

        kernels = []
        for method, namespace, _ in kernel_methods:
            args = []
            for arg in method.parameters[2:]:
                args.append((arg.name, arg.type))

            kernel_params = {
                'kernelname': method.name,
                'kernelnamespace': 'using namespace %s;' % '::'.join(namespace) if namespace else '',
                'args': ',\n          '.join('%s(0, 0, 0)' % arg[1] for i, arg in enumerate(args)),
                'static_variant': ('_' + self.generator.variant_name[1:]) if self.env.STATIC else ''
            }
            kernels.append(template_kernel % kernel_params)

        params = {
            'pch': '#include <%s>\n' % self.generator.pchstop if self.generator.pchstop else '',
            'source': self.generator.kernel_source_path,
            'kernels': '\n'.join(kernels)
        }

        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(template % params)


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
    ast = task_gen.kernel_source
    out = ast.change_ext('.cpu%s.cc' % task_gen.variant_name)
    task_gen.create_task('cpuc', [ast], [out])
    task_gen.source.append(out)


@feature('motor:preprocess')
def create_cpu_kernels(task_gen):
    for kernel, kernel_source, kernel_path, kernel_ast in task_gen.kernels + task_gen.kernels_cpu:
        kernel_gens = {}
        for env in task_gen.bld.multiarch_envs:
            for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
                if kernel_type != 'cpu':
                    continue
                kernel_env = task_gen.bld.all_envs[toolchain]
                for variant in [''] + kernel_env.VECTOR_OPTIM_VARIANTS:
                    tgen = task_gen.bld.get_tgen_by_name(env.ENV_PREFIX % task_gen.parent)
                    target_suffix = '.'.join([kernel_type] + ([variant[1:]] if variant else []))
                    kernel_target = task_gen.parent + '.' + '.'.join(kernel) + '.' + target_suffix
                    kernel_task_gen = task_gen.bld(
                        env=kernel_env.derive(),
                        bld_env=env,
                        target=env.ENV_PREFIX % kernel_target,
                        target_name=env.ENV_PREFIX % task_gen.parent,
                        safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                        variant_name=variant,
                        kernel=kernel,
                        kernel_source_path=kernel_source.path_from(kernel_path),
                        features=[
                            'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                            'motor:cpu:kernel_create'
                        ],
                        pchstop=tgen.preprocess.pchstop,
                        defines=tgen.defines + [
                            'MOTOR_KERNEL_ID=%s_%s' %
                            (task_gen.parent.replace('.', '_'), kernel_target.replace('.', '_')),
                            'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                            'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                            'MOTOR_KERNEL_ARCH=%s' % variant
                        ],
                        includes=tgen.includes + [kernel_path],
                        kernel_source=kernel_ast,
                        source_nodes=tgen.source_nodes,
                        use=tgen.use + [env.ENV_PREFIX % 'plugin.compute.cpu'] + ([variant] if variant else []),
                        uselib=tgen.uselib,
                    )
                    kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name
                    try:
                        kernel_gens[kernel_target].append(kernel_task_gen)
                    except KeyError:
                        kernel_gens[kernel_target] = [kernel_task_gen]
        for kernel_target, kernel_gen_list in kernel_gens.items():
            task_gen.bld.multiarch(kernel_target, kernel_gen_list)


def build(build_context):
    pass