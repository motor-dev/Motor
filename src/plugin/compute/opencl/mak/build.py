from waflib import Task
from waflib.TaskGen import feature, before_method, extension
from waflib.Tools import c_preproc
import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

template_cc = """
%(pch)s
#include    <motor/config/config.hh>
#include    <motor/kernel/simd.hh>
#include    <motor/kernel/input/input.hh>
#include    <motor/plugin/dynobjectlist.hh>

extern const unsigned char s_%(kernel_name)scldata32[];
extern const unsigned long s_%(kernel_name)scldata32_size;
extern const unsigned char s_%(kernel_name)scldata64[];
extern const unsigned long s_%(kernel_name)scldata64_size;

_MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel32, s_%(kernel_name)scldata32);
_MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel32Size, s_%(kernel_name)scldata32_size);
_MOTOR_PLUGIN_EXPORT_VAR(const unsigned char* s_clKernel64, s_%(kernel_name)scldata64);
_MOTOR_PLUGIN_EXPORT_VAR(const u64 s_clKernel64Size, s_%(kernel_name)scldata64_size);

_MOTOR_REGISTER_PLUGIN(MOTOR_KERNEL_ID, MOTOR_KERNEL_NAME);
_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32);
_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel32Size);
_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64);
_MOTOR_REGISTER_METHOD(MOTOR_KERNEL_ID, s_clKernel64Size);
"""


class embed_cl(Task.Task):
    "embed_cl"
    color = 'CYAN'

    def sig_vars(self):
        self.m.update(template_cc.encode('utf-8'))
        self.m.update((self.generator.pchstop if self.generator.pchstop else '').encode('utf-8'))

    def run(self):
        with open(self.inputs[0].abspath(), 'rb') as input_file:
            kernel_name, includes, source, kernel_methods = pickle.load(input_file)
        params = {
            'pch': '#include <%s>\n' % self.generator.pchstop if self.generator.pchstop else '',
            'kernel_name': kernel_name.replace('.', '_')
        }
        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(template_cc % params)


@feature('motor:preprocess')
def create_cl_kernels(task_gen):
    for kernel, kernel_source, kernel_path, kernel_ast in task_gen.kernels:
        kernel_gens = []
        kernel_target = '.'.join([task_gen.parent, '.'.join(kernel), 'cl'])
        for env in task_gen.bld.multiarch_envs:
            for kernel_type, toolchain in env.KERNEL_TOOLCHAINS:
                if kernel_type != 'opencl':
                    continue
                kernel_env = task_gen.bld.all_envs[toolchain]
                tgen = task_gen.bld.get_tgen_by_name(env.ENV_PREFIX % task_gen.parent)

                kernel_task_gen = task_gen.bld(
                    env=kernel_env.derive(),
                    bld_env=env,
                    target=env.ENV_PREFIX % kernel_target,
                    target_name=env.ENV_PREFIX % task_gen.parent,
                    safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                    kernel=kernel,
                    features=[
                        'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel',
                        'motor:kernel_create', 'motor:cl:kernel_create'
                    ],
                    pchstop=tgen.preprocess.pchstop,
                    defines=tgen.defines + [
                        'MOTOR_KERNEL_ID=%s_%s' % (task_gen.parent.replace('.', '_'), kernel_target.replace('.', '_')),
                        'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                        'MOTOR_KERNEL_TARGET=%s' % kernel_type,
                    ],
                    includes=tgen.includes,
                    kernel_source=kernel_source,
                    kernel_ast=kernel_ast,
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
    source = task_gen.kernel_ast
    cc_source = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.trampoline.cc')
    task_gen.create_task('embed_cl', [source], [cc_source])
    task_gen.source += [cc_source]


@extension('.32.ll', '.64.ll')
def cl_kernel_compile(task_gen, source):
    if 'motor:cl:kernel_create' in task_gen.features:
        ptr_size = source.name[-5:-3]
        cl_source = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.generated.cl')
        cl_cc = task_gen.make_bld_node('src', source.parent, source.name[:source.name.rfind('.')] + '.embedded.cc')

        task_gen.create_task('ircc', [source], [cl_source], ircc_target=task_gen.env.IRCC_CL_TARGET)
        task_gen.create_task(
            'bin2c', [cl_source], [cl_cc],
            var='%scldata%s' % ('_'.join(task_gen.kernel), ptr_size),
            zero_terminate=True
        )
        task_gen.source += [cl_cc]


def build(build_context):
    build_context.env.IRCC_CL_TARGET = build_context.path.find_node('ir2cl')
