import os
import sys
import re
import waflib.Utils
from copy import deepcopy
from typing import Dict, List, Optional, Tuple
from ....options import ConfigurationContext
from ..platform import Platform


def _to_number(version_string: str) -> Tuple[int, ...]:
    v = version_string.split('-')[0].split('.')
    result = [0, 0, 0]
    for i in (0, 1, 2):
        if not v:
            break
        d = v.pop(0)
        try:
            result[i] = int(d)
        except ValueError:
            m = re.match('\\d+', d)
            if m is not None:
                result[i] = int(m.group())
    return tuple(result)


def detect_executable(
        configuration_context: ConfigurationContext,
        program_name: str,
        path_list: Optional[List[str]] = None
) -> Optional[str]:
    program = configuration_context.find_program(program_name, var='TEMP_PROGRAM', path_list=path_list, mandatory=False)
    del configuration_context.env['TEMP_PROGRAM']
    if isinstance(program, list):
        return program[0]
    else:
        return program


def get_sysroot_libpaths(sysroot: str) -> List[str]:
    try:
        ld_confs = [os.path.join(sysroot, 'etc', 'ld.so.conf')] + os.listdir(
            os.path.join(sysroot, 'etc', 'ld.so.conf.d'))
    except OSError:
        return [os.path.join(sysroot, 'usr', x) for x in ('lib32', 'lib64', 'libx32', 'lib')]
    else:
        libpaths = [
            os.path.join(sysroot, 'lib'),
            os.path.join(sysroot, 'lib64'),
            os.path.join(sysroot, 'usr/lib'),
            os.path.join(sysroot, 'usr/lib64')
        ]
        for ld_conf in ld_confs:
            try:
                f = open(os.path.join(sysroot, 'etc', 'ld.so.conf.d', ld_conf), 'r')
            except OSError:
                pass
            else:
                for line in f:
                    line = line.split('#')[0].strip()
                    if not line:
                        continue
                    elif line.startswith('include'):
                        continue
                    elif os.path.isdir(os.path.join(sysroot, line)):
                        libpaths.append(os.path.join(sysroot, line))
        return libpaths


class Compiler(object):
    NAMES = tuple()  # type: Tuple[str,...]
    TOOLS = []  # type: List[str]
    SUPPORTED_ARCHS = [
        'amd64',
        'arm64',
        'arm64e',
        'ppc64',
        'ppc64le',
    ]
    ARCHS = {
        'x86': 'x86',
        'i386': 'x86',
        'i486': 'x86',
        'i586': 'x86',
        'i686': 'x86',
        'amd64': 'amd64',
        'x86_64': 'amd64',
        'x64': 'amd64',
        'arm': 'armv7a',
        'armv6': 'armv6',
        'armv7': 'armv7a',
        'armv7a': 'armv7a',
        'armv7s': 'armv7s',
        'armv7k': 'armv7k',
        'armv7l': 'armv7l',
        'arm64': 'arm64',
        'arm64e': 'arm64e',
        'aarch64': 'arm64',
        'aarch32': 'aarch32',
        'arm64_32': 'arm64_32',
        'aarch64_32': 'arm64_32',
        'ppc': 'ppc',
        'powerpc': 'ppc',
        'ppc64': 'ppc64',
        'powerpc64': 'ppc64',
        'ppc64le': 'ppc64le',
        'powerpc64le': 'ppc64le',
        'spu': 'spu',
        'ia64': 'ia64',
        'itanium': 'ia64',
    }
    VECTORIZED_FLAGS = {}  # type: Dict[str, Tuple[Tuple[str, List[str]], ...]]

    def __init__(
            self,
            compiler_c: str,
            compiler_cxx: str,
            version: str,
            platform: str,
            arch: str,
            extra_args: Optional[Dict[str, List[str]]] = None,
            extra_env: Optional[Dict[str, str]] = None):

        self.compiler_c = compiler_c
        self.compiler_cxx = compiler_cxx
        self.defines = []  # type: List[str]
        self.extra_args = deepcopy(extra_args or {})
        self.extra_args_private = {}  # type: Dict[str, List[str]]
        self.version = version
        self.version_number = _to_number(version)
        self.platform = platform
        self.platform_name = platform.replace('-', '_')
        self.arch = self.to_target_arch(arch)
        self.arch_name = self.arch
        self.siblings = [self]
        self.extra_env = extra_env or {}
        self.env = os.environ.copy()
        for env_name, env_value in self.extra_env.items():
            self.env[env_name] = env_value
        self.directories = [os.path.dirname(compiler_c)]
        self.sysroot = None  # type: Optional[str]
        self.target = ''
        self.targets = []  # type: List[str]

    def load_tools(self,
                   configuration_context: ConfigurationContext,
                   _: Platform) -> None:
        configuration_context.env.CC = self.compiler_c
        configuration_context.env.CXX = self.compiler_cxx
        configuration_context.load(self.TOOLS)

    def add_flags(self, compiler: str, flags: List[str]) -> None:
        try:
            self.extra_args_private[compiler] += waflib.Utils.to_list(flags)[:]
        except KeyError:
            self.extra_args_private[compiler] = waflib.Utils.to_list(flags)[:]

    @classmethod
    def to_target_arch(cls, arch: str) -> str:
        try:
            return cls.ARCHS[arch]
        except KeyError:
            return 'unknown'

    @classmethod
    def run(cls, cmd: List[str], env: Dict[str, str], input_text: Optional[str] = None) -> Tuple[int, str, str]:
        try:
            p = waflib.Utils.subprocess.Popen(
                cmd,
                stdin=waflib.Utils.subprocess.PIPE,
                stdout=waflib.Utils.subprocess.PIPE,
                stderr=waflib.Utils.subprocess.PIPE, env=env
            )
            assert p.stdin is not None
            if input_text is not None:
                p.stdin.write(input_text.encode())
            out, err = p.communicate()
        except Exception as e:
            return -1, '', str(e)
        else:
            if not isinstance(out, str):
                out_str = out.decode(sys.stdout.encoding, errors='ignore')
            else:
                out_str = out
            if not isinstance(err, str):
                err_str = err.decode(sys.stderr.encoding, errors='ignore')
            else:
                err_str = err
            return p.returncode, out_str, err_str

    def run_c(
            self,
            args: List[str],
            input_text: Optional[str] = None,
            env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        return self.run(
            [self.compiler_c] + self.extra_args.get('c', []) + self.extra_args_private.get('c', []) +
            self.extra_args.get('link', []) + self.extra_args_private.get('link', []) + args, env or self.env,
            input_text
        )

    def run_cxx(
            self,
            args: List[str],
            input_text: Optional[str] = None,
            env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        return self.run(
            [self.compiler_cxx] + self.extra_args.get('cxx', []) + self.extra_args_private.get('cxx', []) +
            self.extra_args.get('link', []) + self.extra_args_private.get('link', []) + args, env or self.env,
            input_text
        )

    def sort_name(self) -> Tuple[str, str, Tuple[int, ...], str, str]:
        compiler_name = self.NAMES[0].lower()
        return self.arch, compiler_name, self.version_number, self.arch_name, self.platform_name

    def name(self) -> str:
        compiler_name = self.NAMES[0]
        return '%s-%s-%s-%s' % (compiler_name, self.platform, self.arch_name, self.version)

    def load_in_env(self, configuration_context: ConfigurationContext, platform: Platform) -> None:
        extra_env = list(self.extra_env.items())
        env = configuration_context.env
        env.c_env = extra_env
        env.cxx_env = extra_env
        env.cshlib_env = extra_env
        env.cxxshlib_env = extra_env
        env.cprogram_env = extra_env
        env.cxxprogram_env = extra_env
        env.append_unique('TARGETS', list(self.targets) + [self.target])
        env.append_value('CPPFLAGS', self.extra_args.get('cpp', []))
        env.append_value('CFLAGS', self.extra_args.get('c', []))
        env.append_value('CXXFLAGS', self.extra_args.get('cxx', []))
        env.append_value('LINKFLAGS', self.extra_args.get('link', []))
        env.append_value('CFLAGS', self.extra_args_private.get('c', []))
        env.append_value('CXXFLAGS', self.extra_args_private.get('cxx', []))
        env.append_value('LINKFLAGS', self.extra_args_private.get('link', []))
        env.TARGET_ARCH = self.arch_name
        self.set_optimisation_options(configuration_context)
        self.set_warning_options(configuration_context)

    def set_optimisation_options(self, configuration_context: ConfigurationContext) -> None:
        raise NotImplementedError

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        raise NotImplementedError

    def add_sibling(self, other_compiler: "Compiler") -> None:
        self.siblings.append(other_compiler)

    def find_target_program(
            self,
            configuration_context: ConfigurationContext,
            platform: Platform,
            program: str,
            mandatory: bool = True,
            os_paths: Optional[List[str]] = None,
            var: str = ''
    ) -> None:
        sys_dirs = platform.directories + self.directories
        d, a = os.path.split(self.directories[0])
        while a:
            pd = os.path.join(d, 'bin')
            if os.path.isdir(pd):
                sys_dirs.append(pd)
            d, a = os.path.split(d)
        var = var or program.upper()
        for t in list(self.targets) + [self.target]:
            if configuration_context.find_program('%s-%s' % (t, program), var=var, path_list=sys_dirs, mandatory=False):
                break
        else:
            for t in self.targets:
                if configuration_context.find_program('%s-%s' % (t, program), var=var, mandatory=False):
                    break
            else:
                configuration_context.find_program(program, var=var, path_list=sys_dirs + (os_paths or []),
                                                   mandatory=mandatory)
