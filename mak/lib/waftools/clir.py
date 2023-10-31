import build_framework
import waflib.Errors
import waflib.Node
import waflib.Task
import waflib.TaskGen
import waflib.Tools.ccroot
import waflib.Tools.c_preproc
from build_framework.configure.target.compiler import Clang
from typing import List, Tuple


class clc32(waflib.Task.Task):
    """clc32"""
    run_str = '${CLC_CXX}  -S -emit-llvm -x cl -target spir-unknown-unknown -Xclang -finclude-default-header ' \
              '${CLC_CPPPATH_ST:CLC_KERNEL_HEADER_PATH} ${CLC_CXXFLAGS} ${CLC_CPPPATH_ST:INCPATHS} ' \
              '${CLC_DEFINES_ST:DEFINES} -D_CLC=1 -DMOTOR_COMPUTE ' \
              '${CLC_CXX_SRC_F}${SRC[0].abspath()} ${CLC_CXX_TGT_F} ${TGT}'
    ext_out = ['.32.ll']
    color = 'GREEN'

    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:  # type: ignore
        kernel_nodes = waflib.Tools.ccroot.to_incnodes(self.generator,
                                                       self.generator.to_list(self.env.CLC_KERNEL_HEADER_PATH))
        setattr(self.generator, 'includes_nodes', kernel_nodes + getattr(self.generator, 'includes_nodes'))
        return waflib.Tools.c_preproc.scan(self)


class clc64(waflib.Task.Task):
    """clc64"""
    run_str = '${CLC_CXX}  -S -emit-llvm -x cl -target spir64-unknown-unknown -Xclang -finclude-default-header ' \
              '${CLC_CPPPATH_ST:CLC_KERNEL_HEADER_PATH} ${CLC_CXXFLAGS} ${CLC_CPPPATH_ST:INCPATHS} ' \
              '${CLC_DEFINES_ST:DEFINES} -D_CLC=1 -DMOTOR_COMPUTE ' \
              '${CLC_CXX_SRC_F}${SRC[0].abspath()} ${CLC_CXX_TGT_F} ${TGT}'
    ext_out = ['.64.ll']
    color = 'GREEN'

    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:  # type: ignore
        kernel_nodes = waflib.Tools.ccroot.to_incnodes(self.generator,
                                                       self.generator.to_list(self.env.CLC_KERNEL_HEADER_PATH))
        setattr(self.generator, 'includes_nodes', kernel_nodes + getattr(self.generator, 'includes_nodes'))
        return waflib.Tools.c_preproc.scan(self)


@waflib.TaskGen.feature('motor:kernel_create')
@waflib.TaskGen.before_method('process_source')
def cl_ir_kernel_compile(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.CLC_KERNEL_HEADER_PATH:
        raise waflib.Errors.WafError(
            'environment CLC_KERNEL_HEADER_PATH not set; '
            'make sure setup makes this variable point to the kernel header implementation for this target'
        )
    source = getattr(task_gen, 'kernel_source')  # type: waflib.Node.Node
    out_ll_32 = build_framework.make_bld_node(
        task_gen,
        'src',
        source.parent,
        source.name[:source.name.rfind('.')] + '.32.ll'
    )
    out_ll_64 = build_framework.make_bld_node(
        task_gen,
        'src',
        source.parent,
        source.name[:source.name.rfind('.')] + '.64.ll'
    )

    task_gen.create_task('clc32', [source], [out_ll_32])
    task_gen.create_task('clc64', [source], [out_ll_64])
    task_gen.source += [out_ll_32, out_ll_64]


def configure(configuration_context: build_framework.ConfigurationContext) -> None:
    configuration_context.start_msg('Looking for clang 10+')
    v = configuration_context.env
    for c in Clang.compilers:
        if 'AppleClang' not in c.NAMES and c.version_number >= (10,):
            v.CLC_CXX = c.compiler_cxx
        elif 'AppleClang' in c.NAMES and c.version_number >= (12,):
            v.CLC_CXX = c.compiler_cxx
    if v.CLC_CXX:
        v.CLC_CXXFLAGS = ['-std=clc++', '-g', '-fno-rtti', '-fno-exceptions', '-fno-discard-value-names',
                          '-Wno-unknown-attributes']
        v.CLC_CXXFLAGS_debug = ['-D_DEBUG', '-O0']
        v.CLC_CXXFLAGS_profile = ['-DNDEBUG', '-O2']
        v.CLC_CXXFLAGS_final = ['-DNDEBUG', '-O2']
        v.CLC_CXX_SRC_F = ''
        v.CLC_CXX_TGT_F = ['-o']
        v.CLC_ARCH_ST = ['-arch']
        v.CLC_FRAMEWORKPATH_ST = ['-F%s']
        v.CLC_FRAMEWORK_ST = ['-framework']
        v.CLC_CPPPATH_ST = ['-I']
        v.CLC_DEFINES_ST = ['-D']
        v.CLC_CXXFLAGS_warnnone = ['-w']
        v.CLC_CXXFLAGS_warnall = [
            '-Wall', '-Wextra', '-Wno-invalid-offsetof', '-Werror', '-Wno-sign-compare', '-Woverloaded-virtual',
            '-Wstrict-aliasing'
        ]
    configuration_context.end_msg(configuration_context.env.CLC_CXX)
