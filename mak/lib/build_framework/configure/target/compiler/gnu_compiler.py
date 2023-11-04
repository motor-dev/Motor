import waflib.Configure
import waflib.ConfigSet
import waflib.Errors
import os
import shlex
from copy import deepcopy
from typing import Dict, List, Optional, Tuple
from ....options import ConfigurationContext
from .compiler import Compiler, Platform


def _get_actual_targets(target: str, args: List[str], multilibs: Tuple[Tuple[str, str, List[str]], ...]) -> List[str]:
    target_tuple = target.split('-')
    for arch, flag, archs in multilibs:
        if arch == target_tuple[0]:
            if flag in args:
                return ['-'.join([a] + target_tuple[1:]) for a in archs]
    else:
        return ['-'.join(target_tuple)]


def _split_triple(triple: str) -> Tuple[str, str]:
    content = triple.split('-')
    platform_content = content[-2:]
    for useless in ('pc', 'generic', 'unknown'):
        try:
            platform_content.remove(useless)
        except ValueError:
            pass
    return content[0], '-'.join(platform_content)


def _populate_var(env: waflib.ConfigSet.ConfigSet, language: str, out_text: str, err_text: str) -> None:
    out_lines = err_text.split('\n') + out_text.split('\n')
    while out_lines:
        line = out_lines.pop(0)
        if line.startswith('#include <...>'):
            while out_lines:
                path = out_lines.pop(0).strip()
                if not os.path.isdir(path):
                    break
                env.append_unique('COMPILER_%s_INCLUDES' % language, [os.path.normpath(path)])
        elif line.startswith('#define'):
            line = line[len('#define'):].strip()
            space = line.find(' ')
            if space != -1:
                define = line[:space]
                value = line[space + 1:]
                env.append_unique('COMPILER_%s_DEFINES' % language, ['%s=%s' % (define, value)])


class GnuCompiler(Compiler):
    ALL_ARM_ARCHS = ('armv7a', 'armv7k', 'armv7s')
    ARCH_FLAGS = {
        'x86': ['-msse3', '-mssse3', '-msse4.1', '-msse4.2'],
        'amd64': ['-msse3', '-mssse3', '-msse4.1', '-msse4.2'],
        'arm': ['-march=armv7-a'],
    }
    VECTORIZED_FLAGS = {
        'x86': (
            ('.avx', ['-mavx']),
            ('.avx2', ['-mavx2']),
        ),
        'amd64': (
            ('.avx', ['-mavx']),
            ('.avx2', ['-mavx2']),
        ),
        'ppc': (('.altivec', ['-maltivec']),),
        'ppc64': (('.altivec', ['-maltivec']),),
        'armv6': (('.neon', ['-mfpu=neon']),),
        'armv7a': (('.neon', ['-mfpu=neon']),),
        'armv7s': (('.neon', ['-mfpu=neon']),),
        'armv7k': (('.neon', ['-mfpu=neon']),),
        'armv7l': (('.neon', ['-mfpu=neon']),),
        'arm64': (('.neon', []),),
        'arm64e': (('.neon', []),),
        'aarch32': (('.neon', []),),
    }
    MULTILIBS = {
        'x86': ((['-m64'], 'amd64'),),
        'amd64': ((['-m32'], 'x86'),),
        'ppc': ((['-m64'], 'ppc64'),),
        'ppc64': ((['-m32'], 'ppc'),),
        'ppc64le': ((['-m32'], 'ppc'),),
        'arm': [(['-march=%s' % a], a) for a in ALL_ARM_ARCHS],
        # 'armv4':    [(['-march=%s'%a], a) for a in ALL_ARM_ARCHS],
        # 'armv5':    [(['-march=%s'%a], a) for a in ALL_ARM_ARCHS],
        # 'armv7':    [(['-march=%s'%a], a) for a in ALL_ARM_ARCHS],
        'armv7a': [(['-march=%s' % a], a) for a in ALL_ARM_ARCHS],
        'armv7k': [(['-march=%s' % a], a) for a in ALL_ARM_ARCHS],
        'armv7l': [(['-march=%s' % a], a) for a in ALL_ARM_ARCHS],
    }
    MULTILIB_ARCH_MAP = (
        ('i386', '-m64', ['x86_64']),
        ('i486', '-m64', ['x86_64']),
        ('i586', '-m64', ['x86_64']),
        ('i686', '-m64', ['x86_64']),
        ('x86_64', '-m32', ['i386', 'i486', 'i586', 'i686']),
    )
    MACRO_ARCHS = (
        (('__x86_64__',), 'amd64'),
        (('__i386__',), 'x86'),
        (('__i486__',), 'x86'),
        (('__i586__',), 'x86'),
        (('__i686__',), 'x86'),
        (('__powerpc__',), 'ppc'),
        (('__POWERPC__',), 'ppc'),
        (('__powerpc__', '__powerpc64__', '__BIG_ENDIAN__'), 'ppc64'),
        (('__POWERPC__', '__ppc64__', '__BIG_ENDIAN__'), 'ppc64'),
        (('__powerpc__', '__powerpc64__', '__LITTLE_ENDIAN__'), 'ppc64le'),
        (('__POWERPC__', '__ppc64__', '__LITTLE_ENDIAN__'), 'ppc64le'),
        (('__arm64e__',), 'arm64e'),
        (('__aarch64__', '__ILP32__'), 'arm64_32'),
        (('__aarch64__',), 'aarch64'),
        (('__aarch64',), 'aarch64'),
        (('__aarch32__',), 'aarch32'),
        (('__arm__',), 'armv4'),
        (('__arm__', '__ARM_ARCH_5__'), 'armv5'),
        (('__arm__', '__ARM_ARCH_6__'), 'armv6'),
        (('__arm__', '__ARM_ARCH_6K__'), 'armv6'),
        (('__arm__', '__ARM_ARCH_6Z__'), 'armv6'),
        (('__arm__', '__ARM_ARCH_6KZ__'), 'armv6'),
        (('__arm__', '__ARM_ARCH_6ZK__'), 'armv6'),
        (('__arm__', '__ARM_ARCH_7A__', '__ARM_ARCH_7K__'), 'armv7k'),
        (('__arm__', '__ARM_ARCH_7S__'), 'armv7s'),
        (('__arm__', '__ARM_ARCH_7A__'), 'armv7a'),
    )
    ARCHIVER = 'ar'
    DEFINES = ['_WIN32', '_WIN64', '_M_AMD64', '_M_ARM', '_M_ARM_ARMV7VE', '_M_ARM_FP', '_M_ARM64', '_M_ARM64EC',
               '_M_IX86', '_M_IX86_FP', '_M_X64', '__LP64__', '__ILP32__', '__BIG_ENDIAN__', '__LITTLE_ENDIAN__',
               '__x86_64__', '__i386__', '__i486__', '__i586__', '__i686__', '__powerpc__', '__powerpc64__',
               '__POWERPC__', '__ppc64__', '__arm64e__', '__aarch64__', '__aarch64__', '__aarch64', '__aarch32__',
               '__arm__', '__ARM_ARCH_5__', '__ARM_ARCH_6__', '__ARM_ARCH_6K__', '__ARM_ARCH_6Z__', '__ARM_ARCH_6KZ__',
               '__ARM_ARCH_6ZK__', '__ARM_ARCH_7A__', '__ARM_ARCH_7K__', '__ARM_ARCH_7S__', '__ARM_ARCH_7A__',
               '_CALL_ELF']
    ERROR_FLAGS = ['-Werror']

    def __init__(
            self,
            compiler_c: str,
            compiler_cxx: str,
            extra_args: Optional[Dict[str, List[str]]] = None,
            extra_env: Optional[Dict[str, str]] = None) -> None:
        extra_env = dict(extra_env or {})
        extra_env['LC_ALL'] = 'C'
        extra_env['LANG'] = 'C'
        extra_args = deepcopy(extra_args or {})
        sysroot, names, targets, version, platform, arch = self._get_version(compiler_cxx, extra_args, extra_env or {})
        Compiler.__init__(
            self, compiler_c, compiler_cxx, version, platform, arch, extra_args, extra_env
        )
        self.sysroot = sysroot
        if names is not None:
            self.NAMES = names
        self.targets = targets
        self.target = targets[0]

    @classmethod
    def _get_version(
            cls,
            compiler_c: str,
            extra_args: Dict[str, List[str]],
            extra_env: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[Tuple[str, ...]], List[str], str, str, str]:
        names = None  # type: Optional[Tuple[str, ...]]
        sysroot = None  # type: Optional[str]
        env = os.environ.copy()
        for env_name, env_value in extra_env.items():
            env[env_name] = env_value

        arch = ''
        result, out, err = cls.run([compiler_c] + extra_args.get('c', []) + ['-dumpmachine'], env=env)
        if result == 0:
            target = out.strip()
        else:
            result, out, err = cls.run([compiler_c] + extra_args.get('c', []) + ['-v'], env=env)
            for line in err.split('\n') + out.split('\n'):
                line = line.strip()
                if line.startswith('Target: '):
                    target = line[len('Target: '):]
        targets = _get_actual_targets(target, extra_args.get('c', []), cls.MULTILIB_ARCH_MAP)
        for t in targets[:]:
            targets.append(t.replace('-unknown', ''))
            targets.append(t.replace('--', '-'))
        if targets[0].find('-') != -1:
            arch, platform = _split_triple(targets[0])
        else:
            platform = targets[0]
        if arch:
            try:
                extra_args['c'] += cls.ARCH_FLAGS.get(arch, [])
            except KeyError:
                extra_args['c'] = cls.ARCH_FLAGS.get(arch, [])
            try:
                extra_args['cxx'] += cls.ARCH_FLAGS.get(arch, [])
            except KeyError:
                extra_args['cxx'] = cls.ARCH_FLAGS.get(arch, [])
            try:
                extra_args['link'] += cls.ARCH_FLAGS.get(arch, [])
            except KeyError:
                extra_args['link'] = cls.ARCH_FLAGS.get(arch, [])
        result, out, err = cls.run(
            [compiler_c] + extra_args.get('c', []) + ['-v', '-dM', '-E', '-'], input_text='\n', env=env
        )
        macros = set()
        version = ''
        if result != 0:
            raise waflib.Errors.WafError(
                'Error running %s:\nresult: %d\nstdout: %s\nstderr: %s\n' % (compiler_c, result, out, err))
        lines = err.split('\n') + out.split('\n')
        for line in lines:
            for name in cls.NAMES:
                if line.find('%s version ' % name.lower()) != -1:
                    words = line.split()
                    if 'Apple' in words:
                        names = ('Apple' + cls.NAMES[0],) + cls.NAMES
                    while words[0] != name.lower() and words[1] != 'version':
                        words.pop(0)
                    version = words[2].split('-')[0]
            if line.find('Apple LLVM version ') != -1:
                words = line.split()
                while words[0] != 'Apple' and words[1] != 'LLVM' and words[2] != 'version':
                    words.pop(0)
                version = words[3].split('-')[0]
                names = ('Apple' + cls.NAMES[0],) + cls.NAMES
            if line.startswith('#define'):
                macro = line.split()[1].strip()
                macros.add(macro)
            sysroot_index = line.find('-isysroot')
            if sysroot_index != -1:
                sysroot = shlex.split(line[sysroot_index:].replace('\\', '\\\\'))[1]
                sysroot = os.path.normpath(sysroot)
                if names is None:
                    names = ('cross_' + cls.NAMES[0],) + cls.NAMES

        best = 0
        for values, a in cls.MACRO_ARCHS:
            for v in values:
                if v not in macros:
                    break
            else:
                if len(values) > best:
                    best = len(values)
                    arch = a
        if not best:
            raise waflib.Errors.WafError('could not find architecture')
        return sysroot, names, targets, version, platform, arch

    def is_valid(
            self,
            configuration_context: ConfigurationContext,
            extra_flags: Optional[List[str]] = None
    ) -> bool:
        node = configuration_context.bldnode.make_node('main.cxx')
        tgtnode = node.change_ext('')
        node.write('int main() {}\n')
        try:
            result, out, err = self.run_cxx(
                [node.abspath(), '-std=c++14', '-c', '-o', tgtnode.abspath()] + (extra_flags or []))
        except OSError:
            # print(e)
            return False
        finally:
            node.delete()
            tgtnode.delete()
        return result == 0

    def get_multilib_compilers(self) -> List["GnuCompiler"]:
        try:
            multilibs = self.MULTILIBS[self.arch]
        except KeyError:
            return []
        else:
            result = []
            for multilib in multilibs:
                try:
                    c = self.__class__(
                        self.compiler_c,
                        self.compiler_cxx, {
                            'c': self.extra_args.get('c', []) + multilib[0],
                            'cxx': self.extra_args.get('cxx', []) + multilib[0],
                            'link': self.extra_args.get('link', []) + multilib[0],
                        },
                        extra_env=deepcopy(self.extra_env)
                    )
                    result.append(c)
                except waflib.Errors.WafError:
                    # print(e)
                    pass
            return result

    def set_optimisation_options(self, configuration_context: ConfigurationContext) -> None:
        v = configuration_context.env
        if 'Clang' in self.NAMES:
            v.append_unique('CXXFLAGS_debug', ['-fno-threadsafe-statics'])
            v.append_unique('CXXFLAGS_profile', ['-fno-threadsafe-statics'])
            v.append_unique('CXXFLAGS_final', ['-fno-threadsafe-statics'])
        if 'GCC' in self.NAMES and self.version_number >= (4,):
            v.append_unique('CXXFLAGS_debug', ['-fno-threadsafe-statics'])
            v.append_unique('CXXFLAGS_profile', ['-fno-threadsafe-statics'])
            v.append_unique('CXXFLAGS_final', ['-fno-threadsafe-statics'])
        v.CPPFLAGS_debug = ['-D_DEBUG'] + v.CPPFLAGS_debug
        v.CFLAGS_debug = ['-pipe', '-g', '-D_DEBUG'] + v.CFLAGS_debug
        v.CXXFLAGS_debug = ['-pipe', '-g', '-D_DEBUG'] + v.CXXFLAGS_debug
        v.ASFLAGS_debug = ['-pipe', '-g', '-D_DEBUG'] + v.ASFLAGS_debug
        v.LINKFLAGS_debug = ['-pipe', '-g'] + v.LINKFLAGS_debug
        v.CXXFLAGS_debug_nortc = ['-fno-exceptions']

        v.CPPFLAGS_profile = ['-DNDEBUG'] + v.CPPFLAGS_profile
        v.CFLAGS_profile = ['-pipe', '-g', '-DNDEBUG', '-O3'] + v.CFLAGS_profile
        v.CXXFLAGS_profile = [
                                 '-pipe', '-Wno-unused-parameter', '-g', '-DNDEBUG', '-O3', '-fno-rtti',
                                 '-fno-exceptions'
                             ] + v.CXXFLAGS_profile
        v.ASFLAGS_profile = ['-pipe', '-g', '-DNDEBUG', '-O3'] + v.ASFLAGS_profile
        v.LINKFLAGS_profile = ['-pipe', '-g'] + v.LINKFLAGS_profile

        v.CXXFLAGS_exception = ['-fexceptions']
        v.CXXFLAGS_rtti = ['-frtti']

        v.CPPFLAGS_final = ['-DNDEBUG'] + v.CPPFLAGS_final
        v.CFLAGS_final = ['-pipe', '-g', '-DNDEBUG', '-O3'] + v.CFLAGS_final
        v.CXXFLAGS_final = [
                               '-pipe', '-Wno-unused-parameter', '-g', '-DNDEBUG', '-O3', '-fno-rtti', '-fno-exceptions'
                           ] + v.CXXFLAGS_final
        v.ASFLAGS_final = ['-pipe', '-g', '-DNDEBUG', '-O3'] + v.ASFLAGS_final
        v.LINKFLAGS_final = ['-pipe', '-g'] + v.LINKFLAGS_final

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        v = configuration_context.env
        v.CFLAGS_warnnone = ['-w'] + v.CFLAGS_warnnone
        v.CXXFLAGS_warnnone = ['-w'] + v.CXXFLAGS_warnnone
        if 'Clang' in self.NAMES or 'GCC' in self.NAMES and self.version_number >= (
                3,
                4,
        ):
            extra_flags_c = ['-Wextra']
            extra_flags_cxx = ['-Wextra', '-Wno-invalid-offsetof']
        else:
            extra_flags_c = extra_flags_cxx = []
        if 'GCC' in self.NAMES and self.version_number >= (12,):
            extra_flags_cxx.append('-Wno-attributes=motor::')
        elif 'Clang' in self.NAMES:
            extra_flags_cxx.append('-Wno-unknown-attributes')
        else:
            extra_flags_cxx.append('-Wno-attributes')
        v.CFLAGS_warnall = ['-std=c99', '-Wall'] + extra_flags_c + [
            '-pedantic',
            '-Winline',
            '-Werror',
            '-Wstrict-aliasing',
        ] + v.CFLAGS_warnall
        v.CXXFLAGS_warnall = ['-Wall'] + extra_flags_cxx + [
            '-Werror',
            '-Wno-sign-compare',
            '-Woverloaded-virtual',
            '-Wstrict-aliasing',
        ] + v.CXXFLAGS_warnall
        v.CFLAGS_werror = ['-Werror']
        v.CXXFLAGS_werror = ['-Werror']

    def load_tools(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        os_paths = os.environ['PATH'].split(os.pathsep)
        env = configuration_context.env
        self.find_target_program(configuration_context, platform, self.ARCHIVER, var='AR', os_paths=os_paths)
        self.find_target_program(configuration_context, platform, 'strip', os_paths=os_paths)
        self.find_target_program(configuration_context, platform, 'objcopy', mandatory=False, os_paths=os_paths)
        self.find_target_program(configuration_context, platform, 'gdb', mandatory=False, os_paths=os_paths)
        if not env.GDB:
            configuration_context.find_program('gdb', var='GDB', mandatory=False)
        self.find_target_program(configuration_context, platform, 'lldb', mandatory=False, os_paths=os_paths)
        if not env.LLDB:
            configuration_context.find_program('lldb', var='LLDB', mandatory=False)
        Compiler.load_tools(self, configuration_context, platform)
        env.CC_TGT_F = ['-c', '-o', '']
        env.CXX_TGT_F = ['-c', '-o', '']
        env.CCLNK_TGT_F = ['-o', '']
        env.CXXLNK_TGT_F = ['-o', '']

    def load_in_env(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        env = configuration_context.env
        env.IDIRAFTER = '-idirafter'
        env.SYSTEM_INCLUDE_PATTERN = '-isystem%s'
        Compiler.load_in_env(self, configuration_context, platform)
        if not env.SYSROT:
            env.SYSROOT = self.sysroot
        env.PATH = self.directories + platform.directories + os.environ['PATH'].split(os.pathsep)

        for variant_name, flags in self.VECTORIZED_FLAGS.get(self.arch, []):
            if self.is_valid(configuration_context, flags + self.ERROR_FLAGS):
                env.append_unique('VECTOR_OPTIM_VARIANTS', [variant_name])
                env['CFLAGS_%s' % variant_name] = flags
                env['CXXFLAGS_%s' % variant_name] = flags

        env.COMPILER_NAME = self.__class__.__name__.lower()
        env.COMPILER_TARGET = self.arch + '-' + self.platform
        self.populate_useful_variables(configuration_context, env.SYSROOT)

        env.CXXFLAGS_cxx98 = ['-std=c++98']
        env.CXXFLAGS_cxx03 = ['-std=c++03']
        env.CXXFLAGS_cxx11 = ['-std=c++11']
        env.CXXFLAGS_cxx14 = ['-std=c++14']
        env.CXXFLAGS_cxx17 = ['-std=c++17']
        env.CXXFLAGS_cxx20 = ['-std=c++20']
        env.CXXFLAGS_cxx23 = ['-std=c++23']

    def populate_useful_variables(
            self,
            configuration_context: ConfigurationContext,
            sysroot: Optional[str]
    ) -> None:
        env = configuration_context.env
        sysroot_flags = sysroot and ['--sysroot', sysroot] or []

        result, out, err = self.run_c(
            sysroot_flags + env['CFLAGS'] + ['-x', 'c', '-v', '-dM', '-E', '-'], '\n')
        if result != 0:
            print('could not retrieve system includes: %s' % err)
        else:
            _populate_var(env, 'C', out, err)
        result, out, err = self.run_cxx(
            sysroot_flags + env['CXXFLAGS'] + ['-std=c++14', '-x', 'c++', '-v', '-dM', '-E', '-'], '\n')
        if result != 0:
            print('could not retrieve system includes: %s' % err)
        else:
            _populate_var(env, 'CXX', out, err)

        result, out, err = self.run_cxx(sysroot_flags + ['-x', 'c++', '-print-search-dirs'])
        if result != 0:
            print('could not retrieve system defines: %s' % str(err))
        else:
            lines = out.split('\n')
            libs = []
            while lines:
                line = lines.pop(0)
                if line and line.startswith('libraries:'):
                    line = line[10:].strip()
                    libs = self.split_path_list(line)
            env.append_unique('SYSTEM_LIBPATHS', libs)
        env.COMPILER_C_FLAGS = env.CFLAGS
        env.COMPILER_CXX_FLAGS = env.CXXFLAGS

    @staticmethod
    def split_path_list(line: str) -> List[str]:
        return line.split(os.pathsep)
