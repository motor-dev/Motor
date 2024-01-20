import os
import sys
import json
import waflib.Errors
import waflib.Utils
from typing import Dict, List, Optional, Tuple
from ....options import ConfigurationContext
from .compiler import get_sysroot_libpaths, detect_executable
from .gnu_compiler import GnuCompiler
from ..platform import Platform


def _get_msvc_build_tools(configuration_context: ConfigurationContext) -> List[Tuple[str, str]]:
    # finds all possible VCToolsInstallDir
    result = []
    products = []
    extra_flag_list = [], ['-products', 'Microsoft.VisualStudio.Product.BuildTools']  # type: Tuple[List[str], ...]
    for extra_flags in extra_flag_list:
        try:
            vswhere = configuration_context.bldnode.make_node('host/win32/bin/vswhere.exe')
            command_line = [vswhere.abspath(), '-format', 'json']
            command_line += extra_flags
            p = waflib.Utils.subprocess.Popen(
                command_line + extra_flags,
                stdin=waflib.Utils.subprocess.PIPE,
                stdout=waflib.Utils.subprocess.PIPE,
                stderr=waflib.Utils.subprocess.PIPE
            )
        except OSError:
            pass
        else:
            out, err = p.communicate()
            if not isinstance(out, str):
                out_str = out.decode(sys.stdout.encoding)
            else:
                out_str = out
            products += json.loads(out_str)
    for product in products:
        vs_path = product['installationPath']
        try:
            with open(
                    os.path.join(vs_path, 'VC', 'Auxiliary', 'Build', 'Microsoft.VCToolsVersion.default.txt'), 'r'
            ) as prop_file:
                version = prop_file.read().strip()
        except OSError:
            pass
        else:
            product = product['productId'].split('.')[-1].lower() + product['catalog']['productLineVersion']
            vc_tools_install_dir = os.path.join(vs_path, 'VC', 'Tools', 'MSVC', version)
            result.append((str(product), str(vc_tools_install_dir)))
    return result


class Clang(GnuCompiler):
    compilers = []  # type: List["GnuCompiler"]
    DEFINES = [] + GnuCompiler.DEFINES
    NAMES = ('Clang',)  # type: Tuple[str, ...]
    TOOLS = ['clang', 'clangxx']

    def __init__(
            self,
            clang: str,
            clangxx: str,
            extra_args: Optional[Dict[str, List[str]]] = None,
            extra_env: Optional[Dict[str, str]] = None
    ) -> None:
        GnuCompiler.__init__(self, clang, clangxx, extra_args, extra_env)
        self.targets.append('llvm')

    def has_arch_flag(self) -> bool:
        # if clang manages to compile, then the -arch keyword was ignored
        return_code = self.run_c(['-arch', 'no arch of that name', '-E', '-'], '\n')
        return return_code[0] != 0

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        GnuCompiler.set_warning_options(self, configuration_context)
        configuration_context.env.CXXFLAGS_warnall.append('-Wno-deprecated-register')
        if 'AppleClang' in self.NAMES:
            if self.version_number >= (6, 22):
                configuration_context.env.CXXFLAGS_warnall.append('-Wno-unused-local-typedefs')
        else:
            if self.version_number >= (6, 0):
                configuration_context.env.CXXFLAGS_warnall.append('-Wno-deprecated-register')
            if self.version_number >= (3, 6):
                configuration_context.env.CXXFLAGS_warnall.append('-Wno-unused-local-typedefs')

    def get_clang_multilib_compilers(
            self, vs_install_paths: List[Tuple[str, str]], sysroots: List[Tuple[str, List[str]]]
    ) -> List[GnuCompiler]:
        result = []  # type: List[GnuCompiler]
        seen = {self.arch}
        if self.has_arch_flag():
            for arch_target, arch_name in sorted(self.ARCHS.items()):
                if arch_name in seen:
                    continue
                try:
                    c = self.__class__(
                        self.compiler_c, self.compiler_cxx, {
                            'c': self.extra_args.get('c', []) + ['-arch', arch_target],
                            'cxx': self.extra_args.get('cxx', []) + ['-arch', arch_target],
                            'link': self.extra_args.get('link', []) + ['-arch', arch_target],
                        }
                    )
                except waflib.Errors.WafError:
                    pass
                else:
                    if c.arch in seen:
                        continue
                    result.append(c)
                    seen.add(c.arch)
        target_tuple = self.target.split('-')
        arch = target_tuple[0]
        if target_tuple[-1] == 'msvc':
            gnu_tuple = '-'.join(target_tuple[:-1] + ['gnu'])
            try:
                c = self.__class__(
                    self.compiler_c, self.compiler_cxx, {
                        'c': self.extra_args.get('c', []) + ['--target=%s' % gnu_tuple],
                        'cxx': self.extra_args.get('cxx', []) + ['--target=%s' % gnu_tuple],
                        'link': self.extra_args.get('link', []) + ['--target=%s' % gnu_tuple],
                    }
                )
            except waflib.Errors.WafError:
                # print(e)
                pass
            else:
                result.append(c)
                result += GnuCompiler.get_multilib_compilers(c)
            if self.version_number >= (5,):
                for product, path in vs_install_paths:
                    try:
                        c = self.__class__(
                            self.compiler_c,
                            self.compiler_cxx, {
                                'c': self.extra_args.get('c', []),
                                'cxx': self.extra_args.get('cxx', []) + ['-fms-compatibility-version=19'],
                                'link': self.extra_args.get('link', []),
                            },
                            extra_env={'VCToolsInstallDir': str(path)}
                        )
                    except waflib.Errors.WafError:
                        pass
                    else:
                        c.NAMES = ('clang_%s' % product,) + c.NAMES
                        result.append(c)
                        for compiler in GnuCompiler.get_multilib_compilers(c):
                            compiler.NAMES = ('clang_%s' % product,) + compiler.NAMES
                            result.append(compiler)
            else:
                result.append(self)
                for compiler in GnuCompiler.get_multilib_compilers(c):
                    result.append(compiler)
        else:
            result.append(self)

            r, out, err = self.run_cxx(['-x', 'c++', '-v', '-E', '-'], '\n')
            lines = out.split('\n') + err.split('\n')
            while lines:
                line = lines.pop(0)
                if line.startswith('#include <...>'):
                    while lines:
                        path = lines.pop(0)
                        if path[0] != ' ':
                            break
                        path = path.strip()
                        if os.path.isdir(path):
                            if os.path.split(path)[1].startswith(arch):
                                path = os.path.dirname(path)
                                for x in os.listdir(path):
                                    triple = x.split('-')
                                    if len(triple) < 2:
                                        continue
                                    if triple[0] not in self.ARCHS:
                                        continue
                                    if os.path.isdir(os.path.join(path, x)) and not x.startswith(arch):
                                        a = self.to_target_arch(triple[0])
                                        if a in seen:
                                            continue
                                        try:
                                            c = self.__class__(
                                                self.compiler_c, self.compiler_cxx, {
                                                    'c': self.extra_args.get('c', []) + ['--target=%s' % x],
                                                    'cxx': self.extra_args.get('cxx', []) + ['--target=%s' % x],
                                                    'link': self.extra_args.get('link', []) + ['--target=%s' % x],
                                                }
                                            )
                                        except waflib.Errors.WafError:
                                            pass
                                        else:
                                            if c.arch in seen:
                                                continue
                                            result.append(c)
                                            seen.add(c.arch)
            if len(result) == 1:
                result += GnuCompiler.get_multilib_compilers(self)
            if self.sysroot is None:
                for sysroot_path, targets in sysroots:
                    for target in targets:
                        try:
                            c = self.__class__(
                                self.compiler_c, self.compiler_cxx, {
                                    'c':
                                        self.extra_args.get('c', []) + [
                                            '--sysroot', sysroot_path, '-gcc-toolchain',
                                            os.path.join(sysroot_path, 'usr'),
                                            '--target=%s' % target, '-Wno-unused-command-line-argument'
                                        ],
                                    'cxx':
                                        self.extra_args.get('cxx', []) + [
                                            '--sysroot', sysroot_path, '-gcc-toolchain',
                                            os.path.join(sysroot_path, 'usr'),
                                            '--target=%s' % target, '-Wno-unused-command-line-argument'
                                        ],
                                    'link':
                                        self.extra_args.get('link', []) + [
                                            '--sysroot', sysroot_path, '-gcc-toolchain',
                                            os.path.join(sysroot_path, 'usr'),
                                            '--target=%s' % target, '-Wno-unused-command-line-argument'
                                        ],
                                }
                            )
                        except waflib.Errors.WafError:
                            pass
                        else:
                            result.append(c)
        return result

    def set_optimisation_options(self, configuration_context: ConfigurationContext) -> None:
        GnuCompiler.set_optimisation_options(self, configuration_context)
        # Thread sanitizer
        v = configuration_context.env
        if self.arch in ('amd64', 'arm64', 'ppc64'):
            if self.version_number >= (3, 2):
                v.append_unique('CFLAGS_tsan', ['-fsanitize=thread', '-DBE_THREAD_SANITIZER=1'])
                v.append_unique('CXXFLAGS_tsan', ['-fsanitize=thread', '-DBE_THREAD_SANITIZER=1'])
                v.append_unique('LINKFLAGS_tsan', ['-fsanitize=thread', '-static-libsan'])
            if self.version_number >= (3, 2):
                v.append_unique('CFLAGS_asan', ['-fsanitize=address'])
                v.append_unique('CXXFLAGS_asan', ['-fsanitize=address'])
                v.append_unique('LINKFLAGS_asan', ['-fsanitize=address', '-static-libsan'])

    def load_in_env(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        GnuCompiler.load_in_env(self, configuration_context, platform)
        env = configuration_context.env

        # Add multiarch directories
        sysroot = env.SYSROOT or '/'
        for target in self.targets:
            include_path = os.path.join(sysroot, 'usr', 'include', target)
            if os.path.isdir(include_path):
                env.append_unique('INCLUDES', [include_path])
            lib_path = os.path.join(sysroot, 'usr', 'lib', target)
            if os.path.isdir(lib_path):
                env.append_unique('SYSTEM_LIBPATHS', [lib_path])
        # Template export was fixed in Clang 3.2
        if self.version_number >= (3, 2):
            if platform.NAME != 'windows':
                env.append_unique('CFLAGS', ['-fvisibility=hidden'])
                env.append_unique('CXXFLAGS', ['-fvisibility=hidden'])
                env.CFLAGS_exportall = ['-fvisibility=default']
                env.CXXFLAGS_exportall = ['-fvisibility=default']
        if self.version_number < (3, 7):
            env.DISABLE_DLLEXPORT = True
        if self.target.endswith('msvc'):
            env.append_unique('CFLAGS_debug', ['-fms-runtime-lib=dll_dbg'])
            env.append_unique('CFLAGS_profile', ['-fms-runtime-lib=dll'])
            env.append_unique('CFLAGS_final', ['-fms-runtime-lib=dll'])
            env.append_unique('CXXFLAGS_debug', ['-fms-runtime-lib=dll_dbg'])
            env.append_unique('CXXFLAGS_profile', ['-fms-runtime-lib=dll'])
            env.append_unique('CXXFLAGS_final', ['-fms-runtime-lib=dll'])
            # Setup does not use vthe dbeug/profile/final features,
            # so avoid adding this flag in teh general flags section
            env.append_unique('LDFLAGS_debug', ['-Wl,-nodefaultlib'])
            env.append_unique('LDFLAGS_profile', ['-Wl,-nodefaultlib'])
            env.append_unique('LDFLAGS_final', ['-Wl,-nodefaultlib'])
            env.append_unique('STLIB_debug', ['msvcrtd', 'vcruntimed', 'ucrtd', 'kernel32'])
            env.append_unique('STLIB_profile', ['msvcrt', 'vcruntime', 'ucrt', 'kernel32'])
            env.append_unique('STLIB_final', ['msvcrt', 'vcruntime', 'ucrt', 'kernel32'])

    @staticmethod
    def split_path_list(line: str) -> List[str]:
        result = []
        try:
            while True:
                index = line.index(':', 3)
                result.append(line[:index])
                line = line[index + 1:]
        except ValueError:
            result.append(line)
        return result


def detect_clang(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    result = []  # type: List[GnuCompiler]
    environ = getattr(configuration_context, 'environ', os.environ)
    bindirs = environ['PATH'].split(os.pathsep) + configuration_context.env.EXTRA_PATH
    libdirs = []
    clangs = []
    for bindir in bindirs:
        for libdir in (os.path.join(bindir, '..', 'lib'), os.path.join(bindir, '..')):
            if os.path.isdir(libdir):
                for x in os.listdir(libdir):
                    if x.startswith('llvm'):
                        b = os.path.normpath(os.path.join(libdir, x, 'bin'))
                        if os.path.isdir(b) and b not in libdirs:
                            libdirs.append(b)

    seen = {}  # type: Dict[str, GnuCompiler]
    msvc_versions = _get_msvc_build_tools(configuration_context)
    for _, msvc_path in msvc_versions:
        llvmdir = os.path.split(msvc_path)[0]
        llvmdir = os.path.split(llvmdir)[0]
        llvmdir = os.path.join(llvmdir, 'Llvm')
        if os.path.isdir(llvmdir):
            bindirs.append(os.path.join(llvmdir, 'bin'))
            for directory in os.listdir(llvmdir):
                if os.path.isdir(os.path.join(llvmdir, directory, 'bin')):
                    bindirs.append(os.path.join(llvmdir, directory, 'bin'))
    if sys.platform == 'win32':
        import winreg
        for p in (r'SOFTWARE\Wow6432node\LLVM\LLVM', r'SOFTWARE\LLVM\LLVM'):
            try:
                llvm_path = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p)
            except OSError:
                pass
            else:
                try:
                    path, _ = winreg.QueryValueEx(llvm_path, '')
                except OSError:
                    pass
                else:
                    bindirs.append(os.path.join(path, 'bin'))
    versions = []
    for libdir in get_sysroot_libpaths('/'):
        clang_dir = os.path.join(libdir, 'clang')
        if os.path.isdir(clang_dir):
            versions += os.listdir(clang_dir)
    for version in [''] + ['-%s' % v for v in versions]:
        for path in libdirs + bindirs:
            clang = detect_executable(configuration_context, 'clang' + version, path_list=[path])
            clangxx = detect_executable(configuration_context, 'clang++' + version, path_list=[path])
            if clang is not None and clangxx is not None:
                clang = os.path.normpath(clang)
                clangxx = os.path.normpath(clangxx)
                try:
                    c = Clang(clang, clangxx)
                except waflib.Errors.WafError:
                    # print(e)
                    pass
                else:
                    if not c.is_valid(configuration_context):
                        continue
                    try:
                        seen[c.name()].add_sibling(c)
                    except KeyError:
                        clangs.append(c)
    for c in clangs:
        for multilib_compiler in c.get_clang_multilib_compilers(msvc_versions, configuration_context.env.SYSROOTS):
            if not multilib_compiler.is_valid(configuration_context):
                continue
            try:
                seen[multilib_compiler.name()].add_sibling(multilib_compiler)
            except KeyError:
                seen[multilib_compiler.name()] = multilib_compiler
                result.append(multilib_compiler)
    Clang.compilers = result
    return result


def configure_compiler_clang(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    configuration_context.start_msg('Looking for clang compilers')
    result = detect_clang(configuration_context)
    configuration_context.end_msg('done')
    return result
