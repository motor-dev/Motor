import os
import waflib.Errors
from typing import Dict, List, Optional, Tuple
from ....options import ConfigurationContext
from .compiler import detect_executable
from .gnu_compiler import GnuCompiler
from ..platform import Platform


class ICC(GnuCompiler):
    DEFINES = []  # type: List[str]
    NAMES = ('ICC',)
    ICC_PLATFORMS = {
        '__gnu_linux__': 'linux-gnu',
        '__APPLE__': 'darwin',
    }
    ICC_ARCHS = {
        '__i386__': 'x86',
        '__x86_64__': 'amd64',
    }
    TOOLS = ['icc', 'icpc']
    VECTORIZED_FLAGS = {
        'x86': (
            ('.sse3', ['-mssse3']),
            ('.sse4', [
                '-msse4.2',
            ]),
            ('.avx', ['-mavx']),
            ('.avx2', ['-march=core-avx2']),
        ),
        'amd64': (
            ('.sse3', ['-mssse3']),
            ('.sse4', [
                '-msse4.2',
            ]),
            ('.avx', ['-mavx']),
            ('.avx2', ['-march=core-avx2']),
        ),
    }
    ARCHIVER = 'xiar'

    @classmethod
    def _get_version(
            cls,
            icc: str,
            extra_args: Dict[str, List[str]],
            extra_env: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[Tuple[str, ...]], List[str], str, str, str]:
        env = os.environ.copy()
        for env_name, env_value in extra_env.items():
            env[env_name] = env_value
        result, out, err = cls.run([icc] + extra_args.get('c', []) + ['-dM', '-E', '-'], env=env, input_text='')
        if result != 0:
            raise Exception('could not run ICC %s (%s)' % (icc, err))
        version = ''
        arch = 'unknown'
        platform = 'unknown'
        for line in out.split('\n'):
            if line.startswith('#define '):
                line = line.strip()[len('#define '):]
                sp = line.find(' ')
                if sp == -1:
                    macro = line
                    value = None
                else:
                    macro = line[:sp]
                    value = line[sp + 1:]
                if macro in cls.ICC_PLATFORMS:
                    platform = cls.ICC_PLATFORMS[macro]
                elif macro in cls.ICC_ARCHS:
                    arch = cls.ICC_ARCHS[macro]
                elif macro == '__INTEL_COMPILER':
                    assert value is not None
                    patch = value[-1]
                    minor = value[-2]
                    major = value[:-2]
                    version = '%s.%s%s' % (major, minor, patch if patch != '0' else '')
        target = '%s-%s' % (arch, platform)
        return None, None, [target], version, platform, arch

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        GnuCompiler.set_warning_options(self, configuration_context)
        configuration_context.env.append_unique('CXXFLAGS_warnall', ['-wd597'])

    def load_in_env(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        GnuCompiler.load_in_env(self, configuration_context, platform)
        v = configuration_context.env
        if platform.NAME == 'Linux':
            if self.arch == 'x86':
                v.append_unique('SYSTEM_LIBPATHS', ['=/usr/lib/i386-linux-gnu'])
                v.append_unique('INCLUDES', ['/usr/include/i386-linux-gnu'])
            elif self.arch == 'amd64':
                v.append_unique('SYSTEM_LIBPATHS', ['=/usr/lib/x86_64-linux-gnu'])
                v.append_unique('INCLUDES', ['/usr/include/x86_64-linux-gnu'])
        v.append_unique('CPPFLAGS', ['-fPIC', '-D__PURE_INTEL_C99_HEADERS__=1'])
        v.append_unique('CFLAGS', ['-fPIC', '-D__PURE_INTEL_C99_HEADERS__=1', '-diag-disable', '1292'])
        v.append_unique('CXXFLAGS', ['-fPIC', '-D__PURE_INTEL_C99_HEADERS__=1', '-diag-disable', '1292'])
        if platform.NAME != 'windows':
            if self.version_number >= (10,):
                v.append_unique('LINKFLAGS', ['-static-intel'])
            else:
                v.append_unique('LINKFLAGS', ['-i-static'])
        if self.version_number >= (11,):
            v.append_unique('CFLAGS',
                            ['-fvisibility=hidden', '-DVISIBILITY_EXPORT=__attribute__((visibility("default")))'])
            v.append_unique('CXXFLAGS',
                            ['-fvisibility=hidden', '-DVISIBILITY_EXPORT=__attribute__((visibility("default")))'])
            v.CFLAGS_exportall = ['-fvisibility=default', '-DVISIBILITY_EXPORT=']
            v.CXXFLAGS_exportall = ['-fvisibility=default', '-DVISIBILITY_EXPORT=']
        else:
            v.CFLAGS = ['-DVISIBILITY_EXPORT=']
            v.CXXFLAGS = ['-DVISIBILITY_EXPORT=']

    def is_valid(
            self,
            configuration_context: ConfigurationContext,
            extra_flags: Optional[List[str]] = None
    ) -> bool:
        node = configuration_context.bldnode.make_node('main.cxx')
        tgtnode = node.change_ext('')
        node.write('#include <iostream>\nint main() {}\n')
        try:
            result, out, err = self.run_cxx([node.abspath(), '-c', '-o', tgtnode.abspath()] + (extra_flags or []))
        except waflib.Errors.WafError:
            return False
        finally:
            node.delete()
            tgtnode.delete()
        if not result:
            for e in err.split('\n'):
                if e.find('command line warning') != -1:
                    result = 1
        return result == 0


def _detect_icc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    environ = getattr(configuration_context, 'environ', os.environ)
    bindirs = environ['PATH'].split(os.pathsep) + configuration_context.env.EXTRA_PATH
    seen = set([])
    result = []  # type: List[GnuCompiler]
    for bindir in bindirs:
        icc = detect_executable(configuration_context, 'icc', path_list=[bindir])
        icpc = detect_executable(configuration_context, 'icpc', path_list=[bindir])
        if icc is not None and icpc is not None:
            try:
                c = ICC(icc, icpc)
            except waflib.Errors.WafError:
                pass
            else:
                if c.name() in seen:
                    continue
                if not c.is_valid(configuration_context):
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


def configure_compiler_icc(configuration_context: ConfigurationContext) -> List[GnuCompiler]:
    configuration_context.start_msg('Looking for intel compilers')
    result = _detect_icc(configuration_context)
    configuration_context.end_msg('done')
    return result
