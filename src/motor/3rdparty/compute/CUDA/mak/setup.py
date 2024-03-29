import sys
import shlex
import build_framework
import waflib.Utils
from typing import List, Tuple

ARCHS = [
    (3, 0),
    (3, 5),
    (3, 7),
    (5, 0),
    (5, 2),
    (5, 3),
    (6, 0),
    (6, 1),
    (6, 2),
    (7, 0),
    (7, 2),
    (7, 5),
    (8, 0),
]


class NvccException(Exception):
    pass


def _run_nvcc(nvcc: List[str], flags: List[str]) -> Tuple[str, str]:
    try:
        p = waflib.Utils.subprocess.Popen(
            nvcc + flags, stdin=waflib.Utils.subprocess.PIPE, stdout=waflib.Utils.subprocess.PIPE,
            stderr=waflib.Utils.subprocess.PIPE
        )
        out, err = p.communicate()
    except OSError as e:
        raise NvccException(str(e))
    else:
        if not isinstance(out, str):
            out_str = out.decode(sys.stdout.encoding, errors='ignore')
        else:
            out_str = out
        if not isinstance(err, str):
            err_str = err.decode(sys.stderr.encoding, errors='ignore')
        else:
            err_str = err
        if p.returncode != 0:
            raise NvccException(err_str)
        return out_str, err_str


_CUDA_SNIPPET = """
#include <cuda_runtime_api.h>
__global__ void kernel_main()
{
}

int main(int argc, const char *argv[])
{
    cudaChooseDevice(0, 0);
    return 0;
}
"""


def _check_nvcc(setup_context: build_framework.SetupContext, nvcc: List[str]) \
        -> Tuple[List[str], List[str], List[Tuple[int, int]]]:
    source_node = setup_context.bldnode.make_node('test.cu')
    dest_node = setup_context.bldnode.make_node('test.obj')
    try:
        source_node.write(_CUDA_SNIPPET)
        out, err = _run_nvcc(
            nvcc,
            setup_context.env.NVCC_CXXFLAGS + ['--std=c++14', '-v', source_node.abspath(), '-o', dest_node.abspath()]
        )
        target_includes = None
        target_libs = None
        for line in out.split('\n') + err.split('\n'):
            if line.startswith('#$ LIBRARIES='):
                target_libs = shlex.split(line.split('=')[1].strip())
            elif line.startswith('#$ INCLUDES='):
                target_includes = shlex.split(line.split('=')[1].strip())
        if target_libs is None:
            raise NvccException('could not deduce target path')
        archs = []
        for a in ARCHS:
            try:
                _run_nvcc(
                    nvcc,
                    setup_context.env.NVCC_CXXFLAGS + ['-std=c++14', '-arch', 'compute_{0}{1}'.format(*a), '--version']
                )
            except NvccException:
                pass
            else:
                archs.append(a)
        if not archs:
            raise NvccException('no viable arch found')
        return target_includes or [], target_libs, archs
    finally:
        source_node.delete()


def setup(setup_context: build_framework.SetupContext) -> None:
    if setup_context.env.PROJECTS:
        setup_context.env['check_CUDA'] = True
    elif setup_context.env.NVCC_COMPILERS:
        build_framework.start_msg_setup(setup_context)
        if setup_context.env.COMPILER_NAME == 'suncc':
            setup_context.end_msg('not available with sunCC', color='YELLOW')
            return
        cuda_toolchain = None
        version = (0,)  # type: Tuple[int,...]
        archs = []  # type: List[Tuple[int, int]]
        toolchain = setup_context.env.TOOLCHAIN
        for version, compiler in setup_context.env.NVCC_COMPILERS[::-1]:
            flags = []
            if version >= (11,):
                flags.append('--allow-unsupported-compiler')
                flags.append('-Wno-deprecated-gpu-targets')
            cuda_toolchain = toolchain + '-cuda{}'.format('.'.join(str(x) for x in version))
            setup_context.setenv(cuda_toolchain, env=setup_context.env.detach())
            v = setup_context.env
            v.NVCC_CXX = compiler
            cxx_compiler = v.CXX[0]
            if v.MSVC_COMPILER:
                cl = setup_context.find_program('cl',
                                                path_list=setup_context.env.MSVC_PATH)
                assert cl is not None
                cxx_compiler = cl[0]
            v.append_value('NVCC_CXXFLAGS', ['--compiler-bindir', cxx_compiler] + flags)
            if v.ARCH_LP64:
                v.append_value('NVCC_CXXFLAGS', ['-m64'])
            else:
                v.append_value('NVCC_CXXFLAGS', ['-m32'])
            carry = False
            for flag in v.CXXFLAGS:
                if flag == '-include':
                    carry = True
                elif carry:
                    v.append_value('NVCC_CXXFLAGS', ['-include', flag])
                    carry = False
                else:
                    v.append_value('NVCC_CXXFLAGS', ['-Xcompiler', flag])
            try:
                include_paths, lib_paths, archs = _check_nvcc(setup_context, compiler)
            except NvccException:
                setup_context.setenv(toolchain)
                del setup_context.all_envs[cuda_toolchain]
                cuda_toolchain = None
            else:
                for a in archs:
                    v.append_value('NVCC_CXXFLAGS', ['-gencode', 'arch=compute_{0}{1},code=sm_{0}{1}'.format(*a)])
                v.append_value(
                    'NVCC_CXXFLAGS', ['-gencode', 'arch=compute_{0}{1},code=compute_{0}{1}'.format(*archs[-1])]
                )

                v.append_value('NVCC_CXXFLAGS', ['-Xcudafe', '--diag_suppress=2803'])
                setup_context.setenv(toolchain)
                setup_context.env.append_value('check_CUDA_cxxflags', include_paths)
                setup_context.env.append_value('check_CUDA_linkflags', lib_paths)
                setup_context.env.append_value('check_CUDA_stlib', ['cudart_static'])
                setup_context.env.append_value('FEATURES', ['CUDA'])
                break
        if cuda_toolchain is not None:
            setup_context.env.append_value('KERNEL_TOOLCHAINS', [('cuda', cuda_toolchain)])
            setup_context.env['check_CUDA'] = True
            setup_context.end_msg(
                'cuda {} [{}]'.format('.'.join(str(x) for x in version), ', '.join('{}.{}'.format(*a) for a in archs)))
        else:
            setup_context.end_msg('not found', color='YELLOW')
