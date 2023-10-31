import os
import re
from ...options import ConfigurationContext
from .platform import Platform
from .compiler import Compiler
from typing import List, Tuple


def _is_valid(configuration_context: ConfigurationContext, compiler: Compiler) -> bool:
    node = configuration_context.bldnode.make_node('main.cxx')
    tgtnode = node.change_ext('')
    node.write('#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n')
    try:
        result, out, err = compiler.run_cxx([node.abspath(), '-o', tgtnode.abspath()])
    except OSError:
        return False
    finally:
        node.delete()
        tgtnode.delete()
    return result == 0


class Linux(Platform):
    NAME = 'Linux'
    SUPPORTED_TARGETS = (
        re.compile('.*-linux-gnu.*'),
        re.compile('^linux-gnu.*'),
        re.compile('.*-linux$'),
        re.compile('^linux$'),
    )

    def __init__(self) -> None:
        Platform.__init__(self)

    def get_available_compilers(
            self,
            configuration_context: ConfigurationContext,
            compiler_list: List["Compiler"]
    ) -> List[Tuple["Compiler", List["Compiler"], "Platform"]]:
        result = []  # type: List[Tuple[Compiler, List[Compiler], Platform]]
        for c in compiler_list:
            for regexp in self.SUPPORTED_TARGETS:
                if regexp.match(c.platform) and _is_valid(configuration_context, c):
                    result.append((c, [], self))
        return result

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        env = configuration_context.env

        env.DEST_OS = 'linux'
        env.ABI = 'elf'
        env.VALID_PLATFORMS = ['linux', 'posix', 'pc']
        env.SYSTEM_NAME = 'linux-gnu'

        env.DEPLOY_ROOTDIR = ''
        env.DEPLOY_BINDIR = 'bin'
        env.DEPLOY_RUNBINDIR = 'lib'
        env.DEPLOY_LIBDIR = 'lib'
        env.DEPLOY_INCLUDEDIR = 'include'
        env.DEPLOY_DATADIR = os.path.join('share', 'motor')
        env.DEPLOY_PLUGINDIR = os.path.join(env.DEPLOY_RUNBINDIR, 'motor')
        env.DEPLOY_KERNELDIR = os.path.join(env.DEPLOY_RUNBINDIR, 'motor')
        env.pymodule_PATTERN = '%s.so'
        env.STRIP_BINARY = True

        if 'SunCC' not in compiler.NAMES:
            env.append_unique('CPPFLAGS', ['-fPIC'])
            env.append_unique('CFLAGS', ['-fPIC'])
            env.append_unique('CXXFLAGS', ['-fPIC'])
            env.COMPILER_ABI = 'gnu'
        else:
            env.COMPILER_ABI = 'sun'
        env.append_unique('DEFINES', ['_GNU_SOURCE'])
        env.append_unique('LDFLAGS', ['-ldl', '-lrt', '-lpthread', '-lm', '-lc'])
        env.append_unique('LINKFLAGS_dynamic', ['-Wl,--export-dynamic', '-Wl,-E', '-Wl,-z,origin'])

    def platform_name(self, compiler: Compiler) -> str:
        return compiler.platform_name


def configure_target_linux(
        _: ConfigurationContext,
        platform_list: List[Platform]
) -> None:
    platform_list.append(Linux())
