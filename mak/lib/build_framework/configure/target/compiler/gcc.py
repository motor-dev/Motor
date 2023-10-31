import os
import platform
import waflib.Configure
import waflib.Context
import waflib.Errors
import waflib.Tools.gcc
import waflib.Tools.gxx
import waflib.Tools.c_config
from .compiler import detect_executable
from .gnu_compiler import GnuCompiler
from ....options import ConfigurationContext
from ..platform import Platform
from typing import Dict, List, Optional, Tuple, Type


@waflib.Configure.conf
def check_gcc_o_space(_: waflib.Context.Context, __: str = 'c') -> None:
    pass


@waflib.Configure.conf
def gcc_modifier_platform(_: waflib.Context.Context) -> None:
    pass


@waflib.Configure.conf
def gxx_modifier_platform(_: waflib.Context.Context) -> None:
    pass


class GCC(GnuCompiler):
    NAMES = ('GCC',)  # type: Tuple[str, ...]
    TOOLS = ['gcc', 'gxx']

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        GnuCompiler.set_warning_options(self, configuration_context)
        v = configuration_context.env
        if self.version_number >= (9,):
            v.CXXFLAGS_warnall.append('-Wno-deprecated-copy')
        if self.version_number >= (4, 8):
            v.CXXFLAGS_warnall.append('-Wno-unused-local-typedefs')

    def load_in_env(
            self,
            configuration_context: ConfigurationContext,
            target_platform: Platform
    ) -> None:
        GnuCompiler.load_in_env(self, configuration_context, target_platform)
        v = configuration_context.env
        v.append_unique('CFLAGS', ['-static-libgcc'])
        v.append_unique('CXXFLAGS', ['-static-libgcc'])
        v.append_unique('LINKFLAGS', ['-static-libgcc'])
        if self.version_number >= (4,):
            if target_platform.NAME != 'windows':
                v.append_unique('CFLAGS', ['-fvisibility=hidden'])
                v.append_unique('CXXFLAGS', ['-fvisibility=hidden'])
                v.CFLAGS_exportall = ['-fvisibility=default']
                v.CXXFLAGS_exportall = ['-fvisibility=default']


class LLVM(GCC):
    DEFINES = ['__GNUC__', '__GNUG__'] + GCC.DEFINES
    NAMES = ('LLVM', 'GCC')


def _find_target_gcc(
        configuration_context: ConfigurationContext,
        bindir: str,
        possible_versions: List[str],
        gcc_name_prefix: str,
        cls: Type[GCC],
        seen: Dict[str, GnuCompiler]
) -> Tuple[Optional[GCC], bool]:
    cc = cxx = None
    for possible_version in possible_versions:
        cc = detect_executable(configuration_context, '%s-gcc%s' % (gcc_name_prefix, possible_version),
                               path_list=[bindir])
        if cc:
            break
    if cc is None:
        for possible_version in possible_versions:
            cc = detect_executable(configuration_context, 'gcc%s' % possible_version, path_list=[bindir])
            if cc:
                break
    for possible_version in possible_versions:
        cxx = detect_executable(configuration_context, '%s-g++%s' % (gcc_name_prefix, possible_version),
                                path_list=[bindir])
        if cxx:
            break
    if cxx is None:
        for possible_version in possible_versions:
            cxx = detect_executable(configuration_context, 'g++%s' % possible_version, path_list=[bindir])
            if cxx:
                break
    if cc and cxx:
        try:
            compiler = cls(cc, cxx)
        except waflib.Errors.WafError:
            return None, False
        else:
            if not compiler.is_valid(configuration_context):
                return None, False
            try:
                seen[compiler.name()].add_sibling(compiler)
            except KeyError:
                seen[compiler.name()] = compiler
                return compiler, True
            else:
                return compiler, False
    else:
        return None, False


def _detect_gcc_version(
        configuration_context: ConfigurationContext,
        bindir: str,
        version: str,
        target: str,
        seen: Dict[str, GnuCompiler]
) -> Tuple[List[GnuCompiler], List[GnuCompiler]]:
    root_compilers = []  # type: List[GnuCompiler]
    gcc_compilers = []  # type: List[GnuCompiler]
    version_split = version.split('.')
    possible_versions = [
        '.'.join(version_split),
        ''.join(version_split),
        '.'.join(version_split[0:2]),
        ''.join(version_split[0:2]),
        version_split[0],
        '-' + '.'.join(version_split),
        '-' + ''.join(version_split),
        '-' + '.'.join(version_split[0:2]),
        '-' + ''.join(version_split[0:2]),
        '-' + version_split[0],
        '',
    ]

    c, is_root = _find_target_gcc(configuration_context, bindir, possible_versions, target, GCC, seen)
    if c:
        gcc_compilers.append(c)
        if is_root:
            root_compilers.append(c)
        result, out, err = c.run_c(['-fplugin=dragonegg', '-E', '-'], '')
        if result == 0:
            c, is_root = _find_target_gcc(configuration_context, bindir, possible_versions, 'llvm', LLVM, seen)
            if c:
                gcc_compilers.append(c)
                if is_root:
                    root_compilers.append(c)
    return root_compilers, gcc_compilers


def _detect_gcc_from_path(
        configuration_context: ConfigurationContext,
        path: str,
        seen: Dict[str, GnuCompiler]
) -> Tuple[List[GnuCompiler], List[GnuCompiler]]:
    root_compilers = []  # type: List[GnuCompiler]
    gcc_compilers = []  # type: List[GnuCompiler]
    for subdir, relative in [
        ('', '../..'), ('lib/gcc', '../../../..'), ('lib64/gcc', '../../../..'), ('gcc', '../../..'),
        ('llvm', '../../..')
    ]:
        libdir = os.path.join(path, subdir)
        if not os.path.isdir(libdir):
            continue
        for target in os.listdir(libdir):
            if not os.path.isdir(os.path.join(libdir, target)):
                continue
            if target in ['.svn', '.cvs']:
                continue
            for version in os.listdir(os.path.join(libdir, target)):
                if not os.path.isdir(os.path.join(libdir, target, version)):
                    continue
                if version in ['.svn', '.cvs']:
                    continue
                if os.path.islink(os.path.join(libdir, target, version)):
                    continue
                bindir = os.path.normpath(os.path.join(libdir, relative, 'bin'))
                _1, _2 = _detect_gcc_version(configuration_context, bindir, version, target, seen)
                root_compilers += _1
                gcc_compilers += _2
    for version in os.listdir(path):
        if os.path.isdir(os.path.join(path, version, 'gcc')):
            for target in os.listdir(os.path.join(path, version, 'gcc')):
                bindir = os.path.normpath(os.path.join(path, '..', '..', 'bin'))
                _1, _2 = _detect_gcc_version(configuration_context, bindir, version, target, seen)
                root_compilers += _1
                gcc_compilers += _2
    return root_compilers, gcc_compilers


def _detect_multilib_compilers(
        configuration_context: ConfigurationContext,
        gcc_compilers: List[GnuCompiler],
        seen: Dict[str, GnuCompiler]
) -> List[GnuCompiler]:
    multilib_compilers = []
    for c in gcc_compilers:
        for multilib_compiler in c.get_multilib_compilers():
            if not multilib_compiler.is_valid(configuration_context):
                continue
            try:
                seen[multilib_compiler.name()].add_sibling(multilib_compiler)
            except KeyError:
                seen[multilib_compiler.name()] = multilib_compiler
                multilib_compilers.append(multilib_compiler)
    for c in gcc_compilers + multilib_compilers:
        for sysroot_path, targets in configuration_context.env.SYSROOTS:
            for target in targets:
                if c.target.startswith(target):
                    try:
                        compiler = c.__class__(
                            c.compiler_c, c.compiler_cxx, {
                                'c': c.extra_args.get('c', []) + ['--sysroot', sysroot_path],
                                'cxx': c.extra_args.get('cxx', []) + ['--sysroot', sysroot_path],
                                'link': c.extra_args.get('link', []) + ['--sysroot', sysroot_path],
                            }
                        )
                    except waflib.Errors.WafError:
                        pass
                    else:
                        try:
                            seen[compiler.name()].add_sibling(compiler)
                        except KeyError:
                            seen[compiler.name()] = compiler
                            multilib_compilers.append(compiler)
    return multilib_compilers


def _get_native_gcc(
        configuration_context: ConfigurationContext,
        seen: Dict[str, GnuCompiler]
) -> List[GnuCompiler]:
    result = []  # type: List[GnuCompiler]
    if platform.uname()[0].lower() == 'freebsd':
        try:
            c = GCC('/usr/bin/gcc', '/usr/bin/g++')
        except waflib.Errors.WafError:
            pass
        else:
            if c.is_valid(configuration_context):
                try:
                    seen[c.name()].add_sibling(c)
                except KeyError:
                    seen[c.name()] = c
                    result.append(c)
                for multilib_compiler in c.get_multilib_compilers():
                    if not multilib_compiler.is_valid(configuration_context):
                        continue
                    try:
                        seen[multilib_compiler.name()].add_sibling(c)
                    except KeyError:
                        seen[multilib_compiler.name()] = multilib_compiler
                        result.append(multilib_compiler)
    return result


def detect_gcc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    environ = getattr(configuration_context, 'environ', os.environ)
    bindirs = environ['PATH'].split(os.pathsep) + configuration_context.env.EXTRA_PATH
    paths = [os.path.normpath(os.path.join(path, '..', 'lib')) for path in bindirs]
    path_set = set([path for path in paths if os.path.isdir(path)])
    for bindir in bindirs:
        try:
            for f in os.listdir(os.path.join(bindir, '..')):
                if os.path.isdir(os.path.join(bindir, '..', f, 'lib')):
                    path_set.add(os.path.normpath(os.path.join(bindir, '..', f, 'lib')))
                if os.path.isdir(os.path.join(bindir, '..', f, 'lib64')):
                    path_set.add(os.path.normpath(os.path.join(bindir, '..', f, 'lib64')))
        except OSError:
            pass
        try:
            for f in os.listdir(os.path.join(bindir, '..', 'lib', 'llvm')):
                if os.path.isdir(os.path.join(bindir, '..', 'lib', 'llvm', f, 'lib')):
                    path_set.add(os.path.normpath(os.path.join(bindir, '..', 'lib', 'llvm', f, 'lib')))
            for f in os.listdir(os.path.join(bindir, '..', 'lib64', 'llvm')):
                if os.path.isdir(os.path.join(bindir, '..', 'lib64', 'llvm', f, 'lib')):
                    path_set.add(os.path.normpath(os.path.join(bindir, '..', 'lib64', 'llvm', f, 'lib')))
        except OSError:
            pass
    path_set = path_set.union(configuration_context.env.ALL_ARCH_LIBPATHS)
    seen = {}  # type: Dict[str, GnuCompiler]
    root_compilers = []
    gcc_compilers = []
    for path in path_set:
        try:
            for lib in os.listdir(path):
                if lib.startswith('gcc'):
                    gcc_lib_path = os.path.join(path, lib)
                    _1, _2 = _detect_gcc_from_path(configuration_context, gcc_lib_path, seen)
                    root_compilers += _1
                    gcc_compilers += _2
                    for version in os.listdir(gcc_lib_path):
                        if os.path.isdir(os.path.join(gcc_lib_path, version, 'gcc')):
                            _1, _2 = _detect_gcc_from_path(
                                configuration_context, os.path.join(gcc_lib_path, version, 'gcc'), seen
                            )
                            root_compilers += _1
                            gcc_compilers += _2
        except OSError:
            pass
    root_compilers += _detect_multilib_compilers(configuration_context, gcc_compilers, seen)
    root_compilers += _get_native_gcc(configuration_context, seen)
    return root_compilers


def configure_compiler_gcc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    configuration_context.start_msg('Looking for gcc compilers')
    result = detect_gcc(configuration_context)
    configuration_context.end_msg('done')
    return result
