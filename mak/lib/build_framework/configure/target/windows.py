import os
import re
import waflib.Configure
from ...options import ConfigurationContext
from .platform import Platform
from .compiler import Compiler, MSVC
from typing import List, Tuple


def _is_valid(
        configuration_context: ConfigurationContext,
        compiler: Compiler,
) -> bool:
    node = configuration_context.bldnode.make_node('main.cxx')
    tgtnode = node.change_ext('')
    node.write('#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n')
    try:
        result, out, err = compiler.run_cxx([node.abspath(), '-x', 'c++', '-o', tgtnode.abspath()])
    except OSError:
        return False
    finally:
        node.delete()
        tgtnode.delete()
    return result == 0


def _is_valid_msvc(
        configuration_context: ConfigurationContext,
        compiler: Compiler,
) -> bool:
    assert isinstance(compiler, MSVC)
    node = configuration_context.bldnode.make_node('main.cxx')
    tgtnode = node.change_ext('.exe')
    node.write('#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n')
    try:
        result, out, err = compiler.run_cxx(
            [node.abspath(), '/nologo'] +
            ['/I%s' % i for i in compiler.includes] +
            ['/link', '/out:%s' % tgtnode.abspath()] + ['/LIBPATH:%s' % l for l in compiler.libdirs]
        )
    except OSError:
        return False
    finally:
        node.delete()
        tgtnode.delete()
    return result == 0


def _find_winres(configuration_context: ConfigurationContext, compiler: Compiler) -> None:
    if not compiler.target.endswith('-msvc'):
        winres = configuration_context.find_program(
            compiler.target + '-windres', var='WINRC', path_list=compiler.directories, mandatory=False
        )
        if not winres:
            winres = configuration_context.find_program('windres', var='WINRC', path_list=compiler.directories,
                                                        mandatory=False)
        if not winres:
            configuration_context.find_program('windres', var='WINRC', mandatory=False)
        configuration_context.load(
            ['winres_patch'],
            tooldir=[os.path.join(configuration_context.motornode.abspath(), 'mak', 'lib', 'waftools')]
        )
        if compiler.arch == 'amd64':
            configuration_context.env.append_unique('WINRCFLAGS', ['--target=pe-x86-64'])
    elif not configuration_context.env.WINRC:
        winres = configuration_context.find_program(
            'llvm-rc', var='WINRC', path_list=compiler.directories, mandatory=True
        )
        configuration_context.env.WINRC_TGT_F = '/fo'
        configuration_context.env.WINRC_SRC_F = ''
        configuration_context.load('winres')


class Windows(Platform):
    NAME = 'windows'
    SUPPORTED_TARGETS = (
        re.compile(r'.*mingw32.*'),
        re.compile(r'.*windows-.*'),
    )

    def __init__(self, configuration_context: ConfigurationContext):
        Platform.__init__(self)
        self.configuration_context = configuration_context

    def get_available_compilers(
            self,
            configuration_context: ConfigurationContext,
            compiler_list: List["Compiler"]
    ) -> List[Tuple["Compiler", List["Compiler"], "Platform"]]:
        result = []  # type: List[Tuple[Compiler, List[Compiler], Platform]]
        for c in compiler_list:
            if c.arch not in c.SUPPORTED_ARCHS:
                continue
            for regexp in self.SUPPORTED_TARGETS:
                if regexp.match(c.platform):
                    if 'Clang' in c.NAMES:
                        if _is_valid(configuration_context, c):
                            result.append((c, [], Windows_Clang(configuration_context)))
                    elif 'GCC' in c.NAMES:
                        if _is_valid(configuration_context, c):
                            result.append((c, [], Windows_GCC(configuration_context)))
                    elif 'msvc' in c.NAMES:
                        if c.arch not in ('ia64',) and _is_valid_msvc(configuration_context, c):
                            result.append((c, [], Windows_MSVC(self.configuration_context)))
                    else:
                        result.append((c, [], self))
        return result

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        env = configuration_context.env
        env.ABI = 'pe'
        env.VALID_PLATFORMS = ['windows', 'pc']
        env.pymodule_PATTERN = '%s.pyd'

        env.DEPLOY_ROOTDIR = ''
        env.DEPLOY_BINDIR = ''
        env.DEPLOY_RUNBINDIR = ''
        env.DEPLOY_LIBDIR = 'lib'
        env.DEPLOY_INCLUDEDIR = 'include'
        env.DEPLOY_DATADIR = 'data'
        env.DEPLOY_PLUGINDIR = 'data/plugin'
        env.DEPLOY_KERNELDIR = 'data/kernel'

        if compiler.arch == 'arm':
            env.MS_PROJECT_PLATFORM = 'ARM'
        elif compiler.arch == 'arm64':
            env.MS_PROJECT_PLATFORM = 'ARM64'
        elif compiler.arch == 'amd64':
            env.MS_PROJECT_PLATFORM = 'x64'
        else:
            env.MS_PROJECT_PLATFORM = 'Win32'

        env.append_unique(
            'DEFINES',
            ['_WIN32_WINNT=0x0502', 'WINVER=0x0502', '_CRT_SECURE_NO_DEPRECATE=1', '_CRT_SECURE_NO_WARNINGS=1']
        )

    def platform_name(self, compiler: Compiler) -> str:
        return compiler.platform_name


class Windows_Clang(Windows):

    def platform_name(self, compiler: Compiler) -> str:
        if not compiler.target.endswith('-msvc'):
            return 'mingw'
        return Windows.platform_name(self, compiler)

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        Windows.load_in_env(self, configuration_context, compiler)
        env = configuration_context.env
        if not compiler.target.endswith('-msvc'):
            env.append_value('DEFINES', ['__MSVCRT_VERSION__=0x0700'])
            env.append_unique('LDFLAGS', ['-Wl,-Bstatic', '-static', '-static-libgcc', '-static-libstdc++',
                                          '-Wl,--enable-auto-import'])
            env.append_unique('CXXFLAGS_debug', ['-fno-exceptions'])
            if compiler.version_number < (3, 8):
                env.append_unique('LINKFLAGS', ['-Wl,--allow-multiple-definition'])
            env.IMPLIB_ST = '-Wl,--out-implib,%s'
            env.DEF_ST = '-Wl,-d,%s'
            env.LINKFLAGS_console = ['-Wl,--subsystem,console']
            env.STRIP_BINARY = True
            env.implib_PATTERN = 'lib%s.a'
            env.COMPILER_ABI = 'mingw'
            env.SYSTEM_NAME = 'w64-mingw32'
        else:
            env.SHLIB_MARKER = []
            env.STLIB_MARKER = []
            env.cstlib_PATTERN = '%s.lib'
            env.cxxstlib_PATTERN = '%s.lib'
            env.implib_PATTERN = '%s.lib'
            env.append_unique('CXXFLAGS_warnall', ['-Wno-microsoft-enum-value', '-Wno-deprecated-register'])
            env.IMPLIB_ST = '-Wl,-implib:%s'
            env.LINKFLAGS_console = ['-Wl,-subsystem:console']
            env.COMPILER_ABI = 'msvc'
            env.CC_NAME = 'clang_msvc'
            env.SYSTEM_NAME = 'pc-win32'
        env.append_unique('CXXFLAGS_warnall', ['-Wno-unknown-pragmas', '-Wno-comment'])
        _find_winres(configuration_context, compiler)
        env.DEFINES_console = ['_CONSOLE=1']
        env.cprogram_PATTERN = '%s.exe'
        env.cxxprogram_PATTERN = '%s.exe'
        env.cshlib_PATTERN = '%s.dll'
        env.cxxshlib_PATTERN = '%s.dll'
        for option in ('-fpic', '-fPIC'):
            try:
                env.CFLAGS_cshlib.remove(option)
            except ValueError:
                pass
            try:
                env.CXXFLAGS_cxxshlib.remove(option)
            except ValueError:
                pass


class Windows_GCC(Windows):

    def platform_name(self, compiler: Compiler) -> str:
        return 'mingw'

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        Windows.load_in_env(self, configuration_context, compiler)
        env = configuration_context.env
        env.append_unique('LDFLAGS', ['-Wl,-Bstatic', '-static', '-static-libgcc', '-static-libstdc++'])
        env.append_unique('CXXFLAGS_warnall', ['-Wno-unknown-pragmas', '-Wno-comment'])
        env.COMPILER_ABI = 'mingw'
        env.SYSTEM_NAME = 'w64-mingw32'
        _find_winres(configuration_context, compiler)
        env.DEFINES_console = ['_CONSOLE=1']
        env.LINKFLAGS_console = ['-mconsole']
        env.STRIP_BINARY = True
        env.cprogram_PATTERN = '%s.exe'
        env.cxxprogram_PATTERN = '%s.exe'
        env.cshlib_PATTERN = '%s.dll'
        env.cxxshlib_PATTERN = '%s.dll'
        env.implib_PATTERN = 'lib%s.a'
        env.IMPLIB_ST = '-Wl,--out-implib,%s'
        env.DEF_ST = '-Wl,-d,%s'
        for option in ('-fpic', '-fPIC'):
            try:
                env.CFLAGS_cshlib.remove(option)
            except ValueError:
                pass
            try:
                env.CXXFLAGS_cxxshlib.remove(option)
            except ValueError:
                pass


class Windows_MSVC(Windows):

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        Windows.load_in_env(self, configuration_context, compiler)
        env = configuration_context.env
        env.DEFINES_console = ['_CONSOLE=1']
        env.LINKFLAGS_console = ['/SUBSYSTEM:console']
        env.IMPLIB_ST = '/IMPLIB:%s'
        env.DEF_ST = '/DEF:%s'
        env.SYSTEM_NAME = 'pc-win32'
        env.COMPILER_ABI = 'msvc'


def configure_target_windows(
        configuration_context: ConfigurationContext,
        platform_list: List[Platform]
) -> None:
    platform_list.append(Windows(configuration_context))
