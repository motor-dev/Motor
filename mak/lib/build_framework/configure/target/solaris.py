import os
import re
from ...options import ConfigurationContext
from .platform import Platform
from .compiler import Compiler
from typing import List, Tuple


def _is_valid(
        configuration_context: ConfigurationContext,
        compiler: Compiler,
        options: List[str]
) -> bool:
    node = configuration_context.bldnode.make_node('main.cxx')
    tgtnode = node.change_ext('')
    node.write('#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n')
    try:
        result, out, err = compiler.run_cxx([node.abspath(), '-o', tgtnode.abspath()] + options)
    except OSError:
        return False
    finally:
        # if result:
        #    print(compiler.name(), err)
        node.delete()
        tgtnode.delete()
    return result == 0


def _get_suncc_system_libpath(configuration_context: ConfigurationContext, compiler: Compiler) -> None:
    node = configuration_context.bldnode.make_node('main.cxx')
    tgtnode = node.change_ext('')
    node.write('int main() {}\n')
    try:
        result, out, err = compiler.run_cxx([node.abspath(), '-o', tgtnode.abspath(), '-###'])
    except Exception as e:
        print(e)
        pass
    else:
        # if result:
        #    print(compiler.name(), err)
        for line in out.split() + err.split():
            if line[0] == '"':
                line = line[1:-1]
            if line[0:2] == 'P,':
                configuration_context.env.append_value('SYSTEM_LIBPATHS', line[2:].split(':'))
    finally:
        node.delete()


class Solaris(Platform):
    NAME = 'Solaris'
    SUPPORTED_TARGETS = (
        re.compile('^solaris.*'),
        re.compile('^sun-solaris.*'),
        re.compile('^sunos.*'),
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
            if c.arch not in c.SUPPORTED_ARCHS:
                continue
            for regexp in self.SUPPORTED_TARGETS:
                if regexp.match(c.platform):
                    if _is_valid(configuration_context, c, ['-std=c++98'] if 'Clang' in c.NAMES else []):
                        result.append((c, [], self))
                        break
            else:
                pass
                # print(c.platform)
        return result

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        env = configuration_context.env

        env.DEST_OS = 'solaris'
        env.ABI = 'elf'
        env.VALID_PLATFORMS = ['solaris', 'sunos', 'posix', 'pc']
        env.SYSTEM_NAME = 'pc-solaris'

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
            if 'Clang' in compiler.NAMES:
                env.append_unique('CXXFLAGS', ['-std=c++98'])
        else:
            env.COMPILER_ABI = 'sun'
            env.append_value('DEFINES', ['__unix__=1'])
            _get_suncc_system_libpath(configuration_context, compiler)
        env.append_unique('DEFINES', ['_GNU_SOURCE'])
        env.append_unique('LDFLAGS', ['-ldl', '-lrt', '-lpthread', '-lm', '-lc'])
        # env.append_unique('LINKFLAGS', ['-rdynamic'])

    def platform_name(self, compiler: Compiler) -> str:
        return 'solaris'


def configure_target_solaris(
        _: ConfigurationContext,
        platform_list: List[Platform]
) -> None:
    platform_list.append(Solaris())
