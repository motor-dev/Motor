import os
import re
from ...options import ConfigurationContext
from .compiler import Compiler
from .platform import Platform
from typing import List, Tuple


class FreeBSD(Platform):
    NAME = 'FreeBSD'
    SUPPORTED_TARGETS = (
        re.compile(r'.*-freebsd[0-9\.]*'),
        re.compile(r'^freebsd[0-9\.]*'),
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
                    # FreeBSD is not really multiarch, check that proper libs are installed
                    tmpnode = configuration_context.bldnode.make_node('a.out')
                    options = []
                    if 'Clang' in c.NAMES:
                        options.append('-std=c++14')
                        options.append('-stdlib=libc++')
                    try:
                        return_code, out, err = c.run_cxx(
                            ['-x', 'c++', '-o', tmpnode.abspath()] + options + ['-'],
                            '#include <iostream>\nint main(int argc, char* argv[]) {  }'
                        )
                        if return_code == 0:
                            result.append((c, [], self))
                    finally:
                        try:
                            tmpnode.delete()
                        except OSError:
                            pass
        return result

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        env = configuration_context.env
        env.DEST_OS = 'freebsd'
        env.ABI = 'elf'
        env.COMPILER_ABI = 'freebsd'
        env.VALID_PLATFORMS = ['freebsd', 'posix', 'pc']
        env.SYSTEM_NAME = 'pc-freebsd'
        sysroot = compiler.sysroot if compiler.sysroot is not None else ''
        env.append_unique('LINKFLAGS', ['-L%s/usr/local/lib' % sysroot])
        ldconfig = '%s/usr/local/libdata/ldconfig' % (compiler.sysroot or '')
        libpaths = []
        try:
            ldconfig_confs = os.listdir(ldconfig)
        except OSError:
            pass
        else:
            for ldconfig_conf in ldconfig_confs:
                with open(os.path.join(ldconfig, ldconfig_conf), 'r') as conf_file:
                    for line in conf_file:
                        if line not in libpaths:
                            libpaths.append('%s%s' % (compiler.sysroot or '', line))
        if 'Clang' in compiler.NAMES:
            env.append_unique('CXXFLAGS', ['-stdlib=libc++'])
            env.append_unique('LINKFLAGS', ['-stdlib=libc++'])

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

        env.append_unique('CPPFLAGS', ['-fPIC'])
        env.append_unique('CFLAGS', ['-fPIC'])
        env.append_unique('CXXFLAGS', ['-fPIC'])
        if env.ARCH_LP64:
            env.RPATH = [':'.join(['$ORIGIN', '$ORIGIN/../', '$ORIGIN/../lib/', '$ORIGIN/../lib/motor/'])]
        else:
            env.RPATH = [
                ':'.join(
                    [
                        '$ORIGIN', '$ORIGIN/../', '$ORIGIN/../lib32/', '$ORIGIN/../lib32/motor/', '$ORIGIN/../lib/',
                        '$ORIGIN/../lib/motor/'
                    ]
                )
            ]

        env.append_unique('LIB', ['rt', 'pthread', 'm'])
        env.append_unique('CFLAGS', ['-I%s/usr/local/include' % (compiler.sysroot or '')])
        env.append_unique('CXXFLAGS', ['-I%s/usr/local/include' % (compiler.sysroot or '')])
        env.append_unique('LIBPATH', libpaths)
        env.append_unique('DEFINES', ['_BSD_SOURCE'])
        env.append_unique('LINKFLAGS_dynamic', ['-rdynamic', '-Wl,-E', '-Wl,-z,origin'])


def configure_target_freebsd(
        _: ConfigurationContext,
        platform_list: List[Platform]
) -> None:
    platform_list.append(FreeBSD())
