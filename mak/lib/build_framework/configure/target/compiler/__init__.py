import waflib.Options
from ....options import ConfigurationContext
from .compiler import Compiler, detect_executable, get_sysroot_libpaths
from .gnu_compiler import GnuCompiler
from .clang import Clang, configure_compiler_clang
from .gcc import GCC, configure_compiler_gcc
from .icc import ICC, configure_compiler_icc
from .msvc import MSVC, configure_compiler_msvc
from .suncc import SunCC, configure_compiler_suncc
from typing import List


def configure_compiler(configuration_context: ConfigurationContext) -> List[Compiler]:
    allowed_compilers = waflib.Options.options.compilers.split(',') if waflib.Options.options.compilers else []
    result = []  # type: List[Compiler]
    if not allowed_compilers or 'clang' in allowed_compilers:
        result += configure_compiler_clang(configuration_context)
    if not allowed_compilers or 'gcc' in allowed_compilers:
        result += configure_compiler_gcc(configuration_context)
    if not allowed_compilers or 'icc' in allowed_compilers:
        result += configure_compiler_icc(configuration_context)
    if not allowed_compilers or 'msvc' in allowed_compilers:
        result += configure_compiler_msvc(configuration_context)
    if not allowed_compilers or 'suncc' in allowed_compilers:
        result += configure_compiler_suncc(configuration_context)
    result.sort(key=lambda x: x.sort_name())
    return result
