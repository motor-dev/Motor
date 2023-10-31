import os
import waflib.Errors
from typing import Dict, List, Optional, Tuple
from ....options import ConfigurationContext
from .compiler import detect_executable
from .gnu_compiler import GnuCompiler
from ..platform import Platform


class SunCC(GnuCompiler):
    DEFINES = []  # type: List[str]
    NAMES = ('SunCC',)
    SUNCC_PLATFORMS = {
        '__gnu_linux__': 'linux-gnu',
        '__gnu__linux__': 'linux-gnu',
        '__sun': 'sunos',
    }
    SUNCC_ARCHS = {
        '__i386': 'x86',
        '__i386__': 'x86',
        '__x86_64__': 'amd64',
    }
    TOOLS = ['suncc', 'suncxx']
    ARCH_FLAGS = {
        'x86':
            [
                '-xarch=sse4_2', '-D__MMX__=1', '-DSSE__=1', '-DSSE2__=1', '-D__SSE3__=1', '-D__SSSE3__=1',
                '-D__SSE4_1__=1', '-D__SSE4_2__=1', '-D__POPCNT__=1'
            ],
        'amd64':
            [
                '-xarch=sse4_2', '-D__MMX__=1', '-DSSE__=1', '-DSSE2__=1', '-D__SSE3__=1', '-D__SSSE3__=1',
                '-D__SSE4_1__=1', '-D__SSE4_2__=1', '-D__POPCNT__=1'
            ],
    }
    VECTORIZED_FLAGS = {
        'x86':
            (
                ('.avx', ['-xarch=sse4_2', '-xarch=avx', '-D__AVX__=1', '-D__XSAVE__=1']),
                ('.avx2', ['-xarch=sse4_2', '-xarch=avx2', '-D__AVX__=1', '-D__XSAVE__=1', '-D__AVX2__=1']),
            ),
        'amd64':
            (
                (
                    '', [
                        '-xarch=sse4_2', '-D__MMX__=1', '-DSSE__=1', '-DSSE2__=1', '-D__SSE3__=1', '-D__SSSE3__=1',
                        '-D__SSE4_1__=1', '-D__SSE4_2__=1', '-D__POPCNT__=1'
                    ]
                ),
                ('.avx', ['-xarch=sse4_2', '-xarch=avx', '-D__AVX__=1', '-D__XSAVE__=1']),
                ('.avx2', ['-xarch=sse4_2', '-xarch=avx2', '-D__AVX__=1', '-D__XSAVE__=1', '-D__AVX2__=1']),
            ),
    }

    def __init__(
            self,
            suncc: str,
            suncxx: str,
            extra_args: Optional[Dict[str, List[str]]] = None,
            extra_env: Optional[Dict[str, str]] = None
    ) -> None:
        GnuCompiler.__init__(self, suncc, suncxx, extra_args, extra_env)
        if self.platform == 'linux-gnu':
            if self.version_number <= (5, 13, 0):
                self.add_flags('cxx', ['-library=Crun,stlport4'])
                self.add_flags('link', ['-library=Crun,stlport4', '-staticlib=Crun,stlport4'])
            if self.arch == 'amd64':
                if os.path.isdir('/lib/x86_64-linux-gnu'):
                    self.add_flags('link', ['-L/lib/x86_64-linux-gnu'])
                if os.path.isdir('/usr/lib/x86_64-linux-gnu'):
                    self.add_flags('link', ['-L/usr/lib/x86_64-linux-gnu'])
            elif self.arch == 'x86':
                for arch in ('i386', 'i486', 'i586', 'i686'):
                    if os.path.isdir('/lib/%s-linux-gnu' % arch):
                        self.add_flags('link', ['-L/lib/%s-linux-gnu' % arch])
                    if os.path.isdir('/usr/lib/%s-linux-gnu' % arch):
                        self.add_flags('link', ['-L/usr/lib/%s-linux-gnu' % arch])

    @classmethod
    def _get_version(
            cls,
            suncxx: str,
            extra_args: Dict[str, List[str]],
            extra_env: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[Tuple[str, ...]], List[str], str, str, str]:
        env = os.environ.copy()
        env.update(extra_env)
        result, out, err = cls.run([suncxx] + extra_args.get('cxx', []) + ['-xdumpmacros', '-E', '/dev/null'], env=env)
        if result != 0:
            raise waflib.Errors.WafError('could not run SunCC %s (%s)' % (suncxx, err))
        version = ''
        arch = 'unknwon'
        platform = 'unknown'
        for line in out.split('\n') + err.split('\n'):
            if line.startswith('#define '):
                line = line.strip()[len('#define '):]
                sp = line.find(' ')
                if sp == -1:
                    macro = line
                    value = None
                else:
                    macro = line[:sp]
                    value = line[sp + 1:]
                if macro in cls.SUNCC_PLATFORMS:
                    platform = cls.SUNCC_PLATFORMS[macro]
                elif macro in cls.SUNCC_ARCHS:
                    arch = cls.SUNCC_ARCHS[macro]
                elif macro == '__SUNPRO_CC':
                    assert value is not None
                    patch = value[-1]
                    minor = value[-3:-1]
                    major = value[2:-3]
                    version = '%s.%s%s' % (major, minor, patch if patch != '0' else '')
        target = '%s-%s' % (arch, platform)
        return None, None, [target], version, platform, arch

    def set_optimisation_options(self, configuration_context: ConfigurationContext) -> None:
        v = configuration_context.env
        v['CPPFLAGS_debug'] = ['-D_DEBUG']
        v['CFLAGS_debug'] = ['-g', '-D_DEBUG']
        v['CXXFLAGS_debug'] = ['-g', '-D_DEBUG']
        v['LINKFLAGS_debug'] = ['-g']

        v['CPPFLAGS_profile'] = ['-DNDEBUG']
        v['CFLAGS_profile'] = ['-g', '-DNDEBUG', '-fast', '-xcache=64/64/2:1024/64/16']
        v['CXXFLAGS_profile'] = [
            '-g', '-DNDEBUG', '-fast', '-features=mutable', '-features=localfor', '-features=bool',
            '-features=no%split_init', '-xcache=64/64/2:1024/64/16'
        ]
        v['LINKFLAGS_profile'] = ['-g']

        v['CPPFLAGS_final'] = ['-DNDEBUG']
        v['CFLAGS_final'] = ['-g', '-DNDEBUG', '-fast', '-xcache=64/64/2:1024/64/16']
        v['CXXFLAGS_final'] = [
            '-g', '-DNDEBUG', '-fast', '-features=mutable', '-features=localfor', '-features=bool',
            '-features=no%split_init', '-xcache=64/64/2:1024/64/16'
        ]
        if self.version_number[0:2] != (5, 13):
            v['CXXFLAGS_profile'] += ['-features=no%except']
            v['CXXFLAGS_final'] += ['-features=no%except']
        v['LINKFLAGS_final'] = ['-g']

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        v = configuration_context.env
        v['CFLAGS_warnnone'] = ['-w', '-errtags=yes', '-erroff=%all']
        v['CXXFLAGS_warnnone'] = ['-w', '-errtags=yes', '-erroff=%all']
        v['CFLAGS_warnall'] = ['-erroff=%none', '-v', '-errtags=yes']
        v['CXXFLAGS_warnall'] = [
            '+w2', '-errtags=yes', '-erroff=fieldsemicolonw,notused,'
                                   'unknownpragma,wunreachable,doubunder,wvarhidenmem,wvarhidemem,'
                                   'reftotemp,truncwarn,badargtype2w,hidef,wemptydecl,notemsource,'
                                   'nonewline,inllargeuse,identexpected,attrskipunsup2'
        ]

        v['CFLAGS_werror'] = ['-errwarn=%all']
        v['CXXFLAGS_werror'] = ['-errwarn=%all']

    def is_valid(
            self,
            configuration_context: ConfigurationContext,
            extra_flags: Optional[List[str]] = None
    ) -> bool:
        node = configuration_context.bldnode.make_node('main.cxx')
        tgtnode = node.change_ext('')
        node.write('#include <cstdlib>\n#include <iostream>\nint main() {}\n')
        try:
            result, out, err = self.run_cxx([node.abspath(), '-c', '-o', tgtnode.abspath()] + (extra_flags or []))
        except waflib.Errors.WafError:
            return False
        finally:
            node.delete()
            tgtnode.delete()
        if not result:
            for msg in err.split('\n'):
                if msg.find('illegal value ignored') != -1:
                    result = 1
        return result == 0

    def load_in_env(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        GnuCompiler.load_in_env(self, configuration_context, platform)
        v = configuration_context.env
        v.SYSTEM_INCLUDE_PATTERN = '-I%s'
        v['RPATH_ST'] = '-R%s'
        v.IDIRAFTER = '-I'
        if platform.NAME == 'Linux':
            if self.arch == 'x86':
                v.append_unique('SYSTEM_LIBPATHS', ['=/usr/lib', '=/usr/lib/i386-linux-gnu'])
                v.CFLAGS += ['-I/usr/include/i386-linux-gnu']
                v.CXXFLAGS += [
                    os.path.join(configuration_context.motornode.abspath(), 'mak/compiler/suncc/interlocked-a=x86.il'),
                    '-xarch=sse2',
                    '-xchip=generic', '-I/usr/include/i386-linux-gnu', '-include', 'math.h'
                ]
            elif self.arch == 'amd64':
                v.append_unique('SYSTEM_LIBPATHS', ['=/usr/lib64', '=/usr/lib/x86_64-linux-gnu'])
                v.CFLAGS += ['-I/usr/include/x86_64-linux-gnu']
                v.CXXFLAGS += [
                    os.path.join(configuration_context.motornode.abspath(),
                                 'mak/compiler/suncc/interlocked-a=amd64.il'), '-xarch=sse2',
                    '-xchip=generic', '-I/usr/include/x86_64-linux-gnu', '-include', 'math.h'
                ]
        else:
            if self.arch == 'x86':
                v.CXXFLAGS += [
                    os.path.join(configuration_context.motornode.abspath(), 'mak/compiler/suncc/interlocked-a=x86.il'),
                    '-xarch=sse2',
                    '-xchip=generic',
                ]
            elif self.arch == 'amd64':
                v.CXXFLAGS += [
                    os.path.join(configuration_context.motornode.abspath(),
                                 'mak/compiler/suncc/interlocked-a=amd64.il'),
                    '-xarch=sse2',
                    '-xchip=generic',
                ]

        v.append_unique('CFLAGS', ['-mt', '-xldscope=hidden', '-Kpic', '-DPIC', '-D__PIC__'])
        v.append_unique('CXXFLAGS', ['-mt', '-xldscope=hidden', '-Kpic', '-DPIC', '-D__PIC__'])
        v.append_unique('LINKFLAGS', ['-lrt', '-mt', '-znow', '-xldscope=hidden'])  # , '-z', 'absexec', '-Kpic'])
        v.CFLAGS_exportall = ['-xldscope=symbolic']
        v.CXXFLAGS_exportall = ['-xldscope=symbolic']
        v.SHLIB_MARKER = '-Bdynamic'
        v.STLIB_MARKER = '-Bstatic'

        v.CXXFLAGS_cxx98 = ['-std=c++03']
        v.CXXFLAGS_cxx03 = ['-std=c++03']
        v.CXXFLAGS_cxx11 = ['-std=c++11']
        v.CXXFLAGS_cxx14 = ['-std=c++14']
        v.CXXFLAGS_cxx17 = ['-std=c++17']
        v.CXXFLAGS_cxx20 = ['-std=c++20']
        v.CXXFLAGS_cxx23 = ['-std=c++23']

        v.TARGETS = self.targets

    def populate_useful_variables(
            self,
            configuration_context: ConfigurationContext,
            sysroot: Optional[str]
    ) -> None:
        compiler_defines = []
        result, out, err = self.run_c(configuration_context.env.CFLAGS + ['-xdumpmacros=defs,loc', '-E', '/dev/null'])
        if result != 0:
            raise Exception('could not run SunC (%s)' % err)
        for line in out.split('\n') + err.split('\n'):
            if line.startswith('command line: #define '):
                line = line.strip()[len('command line: #define '):]
                if line.find('__oracle_') != -1:
                    continue
                sp = line.find(' ')
                if sp == -1:
                    compiler_defines.append(line)
                else:
                    compiler_defines.append('%s=%s' % (line[:sp].strip(), line[sp + 1:].strip()))
        env = configuration_context.env
        env.COMPILER_C_DEFINES = compiler_defines + ['_Pragma(x)=', '__global=']
        main_node = configuration_context.bldnode.make_node('main.c')
        with open(main_node.abspath(), 'w') as main:
            main.write('#include <stdint.h>\n')

        result, out, err = self.run_c(
            env.CXXFLAGS + ['-P', '-H', '-E', '-o/dev/null', main_node.abspath()])

        compiler_includes = []
        for file in err.split('\n'):
            file = file.strip()
            if file:
                pos = file.find('/bits/')
                if pos == -1:
                    pos = file.find('/sys/')
                if pos != -1:
                    directory = file[:pos]
                else:
                    directory = os.path.dirname(file)
                if directory not in compiler_includes:
                    compiler_includes.append(directory)
        if self.arch == 'amd64':
            compiler_includes.append('/usr/include/x86_64-linux-gnu')
        else:
            compiler_includes.append('/usr/include/i386-linux-gnu')
        env.append_unique('COMPILER_C_INCLUDES', compiler_includes)

        compiler_defines = []
        result, out, err = self.run_cxx(env.CXXFLAGS + ['-std=c++14', '-xdumpmacros=defs,loc', '-E', '/dev/null'])
        if result != 0:
            raise Exception('could not run SunCC (%s)' % err)
        for line in out.split('\n') + err.split('\n'):
            if line.startswith('command line: #define '):
                line = line.strip()[len('command line: #define '):]
                sp = line.find(' ')
                if sp == -1:
                    compiler_defines.append(line)
                else:
                    compiler_defines.append('%s=%s' % (line[:sp].strip(), line[sp + 1:].strip()))
        env.COMPILER_CXX_DEFINES = compiler_defines + ['_Pragma(x)=', '__global=']
        main_node = configuration_context.bldnode.make_node('main.cc')
        with open(main_node.abspath(), 'w') as main:
            main.write('#include <cstdint>\n')

        result, out, err = self.run_cxx(
            env.CXXFLAGS + ['-std=c++14', '-P', '-H', '-E', '-o/dev/null', main_node.abspath()])

        compiler_includes = []
        for file in err.split('\n'):
            file = file.strip()
            if file:
                pos = file.find('/bits/')
                if pos == -1:
                    pos = file.find('/sys/')
                if pos != -1:
                    directory = file[:pos]
                else:
                    directory = os.path.dirname(file)
                if directory not in compiler_includes:
                    compiler_includes.append(directory)
        if self.arch == 'amd64':
            compiler_includes.append('/usr/include/x86_64-linux-gnu')
        else:
            compiler_includes.append('/usr/include/i386-linux-gnu')
        env.append_unique('COMPILER_CXX_INCLUDES', compiler_includes)


def _detect_suncc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    result = []  # type: List[GnuCompiler]
    seen = set()
    environ = getattr(configuration_context, 'environ', os.environ)
    bindirs = environ['PATH'].split(os.pathsep) + configuration_context.env.EXTRA_PATH
    for bindir in sorted(bindirs):
        suncc = detect_executable(configuration_context, 'suncc', path_list=[bindir])
        suncxx = detect_executable(configuration_context, 'sunCC', path_list=[bindir])
        if suncc and suncxx:
            c = SunCC(suncc, suncxx)
            if c.name() in seen:
                continue
            if not c.is_valid(configuration_context, ['-D_GNU_SOURCE']):
                continue
            seen.add(c.name())
            result.append(c)
            for multilib_compiler in c.get_multilib_compilers():
                if multilib_compiler.name() in seen:
                    continue
                if not multilib_compiler.is_valid(configuration_context):
                    continue
                seen.add(multilib_compiler.name())
                result.append(multilib_compiler)
    return result


def configure_compiler_suncc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    configuration_context.start_msg('Looking for suncc compilers')
    result = _detect_suncc(configuration_context)
    configuration_context.end_msg('done')
    return result
