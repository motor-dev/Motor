import os
import re
import sys
import waflib.Configure
import waflib.Context
import waflib.Errors
import waflib.Logs
import waflib.Utils
import waflib.Tools.msvc
from typing import Dict, List, Set, Tuple, Union
from ....options import ConfigurationContext
from .compiler import Compiler, detect_executable
from ..platform import Platform

MSVC_PREDEFINED_MACROS = (
    '__cplusplus',
    '__STDC__',
    '__STDC_HOSTED__',
    '__STDC_NO_ATOMICS__',
    '__STDC_NO_COMPLEX__',
    '__STDC_NO_THREADS__',
    '__STDC_NO_VLA__',
    '__STDC_VERSION__',
    '__STDCPP_DEFAULT_NEW_ALIGNMENT__',
    '__STDCPP_THREADS__',
    '__ATOM__',
    '__AVX__',
    '__AVX2__',
    '__AVX512BW__',
    '__AVX512CD__',
    '__AVX512DQ__',
    '__AVX512F__',
    '__AVX512VL__',
    '_CHAR_UNSIGNED',
    '__CLR_VER',
    '_CONTROL_FLOW_GUARD',
    '__cplusplus_cli',
    '__cplusplus_winrt',
    '_CPPRTTI',
    '_CPPUNWIND',
    '_DEBUG',
    '_DLL',
    '_INTEGRAL_MAX_BITS',
    '_ISO_VOLATILE',
    '_M_AMD64',
    '_M_ARM',
    '_M_ARM_ARMV7VE',
    '_M_ARM_FP',
    '_M_ARM64',
    '_M_ARM64EC',
    '_M_CEE',
    '_M_CEE_PURE',
    '_M_CEE_SAFE',
    '_M_FP_CONTRACT',
    '_M_FP_EXCEPT',
    '_M_FP_FAST',
    '_M_FP_PRECISE',
    '_M_FP_STRICT',
    '_M_IX86',
    '_M_IX86_FP',
    '_M_X64',
    '_MANAGED',
    '_MSC_BUILD',
    '_MSC_EXTENSIONS',
    '_MSC_FULL_VER',
    '_MSC_VER',
    '_MSVC_LANG',
    '__MSVC_RUNTIME_CHECKS',
    '_MSVC_TRADITIONAL',
    '_MT',
    '_NATIVE_WCHAR_T_DEFINED',
    '_OPENMP',
    '_PREFAST_',
    '__SANITIZE_ADDRESS__',
    '__TIMESTAMP__',
    '_VC_NODEFAULTLIB',
    '_WCHAR_T_DEFINED',
    '_WIN32',
    '_WIN64',
    '_WINRT_DLL',
)


class MSVC(Compiler):

    def __init__(
            self,
            cl: str,
            name: str,
            version: str,
            target_arch: str,
            arch: str,
            bat: str,
            args: str,
            path: List[str],
            includes: List[str],
            libdirs: List[str]
    ) -> None:
        self.NAMES = (name, 'msvc')
        Compiler.__init__(
            self, cl, cl, version, 'windows-%s' % name, arch, {}, {'PATH': ';'.join(path)}
        )
        self.batfile = bat
        self.path = [p for p in path if p not in os.environ.get('PATH', '').split(os.pathsep)]
        self.args = args
        self.arch_name = target_arch
        self.includes = [
                            os.path.join(i, target_arch) for i in includes if
                            os.path.isdir(os.path.join(i, target_arch))
                        ] + includes
        self.libdirs = libdirs
        self.target = self.platform
        self.platform_name = 'windows'
        self.targets = [self.target]

    def set_optimisation_options(self, configuration_context: ConfigurationContext) -> None:
        env = configuration_context.env
        env.append_unique('CFLAGS_debug', ['/Od', '/Ob1', '/MDd', '/D_DEBUG', '/GR'])
        env.append_unique('CFLAGS_debug_rtc', ['/RTC1', '/RTCc', '/D_ALLOW_RTCc_IN_STL=1'])
        env.append_unique('CXXFLAGS_debug', ['/Od', '/Ob1', '/MDd', '/D_DEBUG', '/GR', '/EHsc'])
        env.append_unique('CXXFLAGS_debug_rtc', ['/RTC1', '/RTCc', '/D_ALLOW_RTCc_IN_STL=1'])
        env.append_unique('CFLAGS', ['/DEBUG', '/Z7'])
        env.append_unique('CXXFLAGS', ['/DEBUG', '/Z7'])
        env.append_unique('LINKFLAGS', ['/DEBUG', '/INCREMENTAL:no'])

        env.append_unique('CFLAGS_profile', ['/DNDEBUG', '/MD', '/O2', '/Oy-', '/GT', '/GF', '/Gy', '/GR-'])
        env.append_unique(
            'CXXFLAGS_profile', ['/DNDEBUG', '/D_HAS_EXCEPTIONS=0', '/MD', '/O2', '/Oy-', '/GT', '/GF', '/Gy', '/GR-']
        )
        env.append_unique('LINKFLAGS_profile', ['/INCREMENTAL:no'])
        env.append_unique('ARFLAGS_profile', [])

        env.append_unique('CFLAGS_final', ['/DNDEBUG', '/MD', '/O2', '/GT', '/GF', '/Gy', '/GR-'])
        env.append_unique(
            'CXXFLAGS_final', ['/DNDEBUG', '/D_HAS_EXCEPTIONS=0', '/MD', '/O2', '/GT', '/GF', '/Gy', '/GR-']
        )
        env.append_unique('LINKFLAGS_final', ['/INCREMENTAL:no'])
        env.append_unique('ARFLAGS_final', [])

        if self.arch == 'x86':
            env.append_unique('CFLAGS', ['/arch:SSE2'])
            env.append_unique('CXXFLAGS', ['/arch:SSE2'])
        if self.NAMES[0] != 'msvc' or self.version_number >= (8,):
            env.append_unique('CFLAGS_profile', ['/GS-'])
            env.append_unique('CXXFLAGS_profile', ['/GS-'])
            env.append_unique('CFLAGS_final', ['/GS-'])
            env.append_unique('CXXFLAGS_final', ['/GS-'])
        if self.NAMES[0] != 'intel' or self.version_number >= (9, 1):
            env.append_unique('CXXFLAGS_cxxstlib', ['/Zl'])
            env.append_unique('CFLAGS_cxxstlib', ['/Zl'])

    def set_warning_options(self, configuration_context: ConfigurationContext) -> None:
        env = configuration_context.env
        if self.NAMES[0] == 'intel':
            env.append_unique('CXXFLAGS', ['/Zc:forScope'])
            if self.version_number >= (11,):
                warning = ['/W4', '/Qdiag-disable:remark']
            else:
                warning = ['/W3']
        else:
            warning = ['/W4']
        env.append_unique('CFLAGS_warnall', warning + ['/D_CRT_SECURE_NO_WARNINGS=1'])
        env.append_unique('CFLAGS_warnnone', ['/D_CRT_SECURE_NO_WARNINGS=1', '/W0'])
        env.append_unique('CFLAGS_werror', ['/WX'])
        env.append_unique('CXXFLAGS_warnall', warning + ['/D_CRT_SECURE_NO_WARNINGS=1'])
        env.append_unique('CXXFLAGS_warnnone', ['/D_CRT_SECURE_NO_WARNINGS=1', '/W0'])
        env.append_unique('CXXFLAGS_werror', ['/WX'])
        if self.NAMES[0] == 'msvc' and self.version_number >= (14,):
            env.append_unique('CFLAGS_warnall', ['/D_ALLOW_RTCc_IN_STL=1'])
            env.append_unique('CXXFLAGS_warnall', ['/D_ALLOW_RTCc_IN_STL=1'])
            env.append_unique('CFLAGS_warnnone', ['/D_ALLOW_RTCc_IN_STL=1'])
            env.append_unique('CXXFLAGS_warnnone', ['/D_ALLOW_RTCc_IN_STL=1'])

    def load_tools(self,
                   configuration_context: ConfigurationContext,
                   _: Platform) -> None:
        env = configuration_context.env
        version = '%s %s' % (self.NAMES[0], self.version)
        version_number = tuple(int(i) for i in self.version.split('.'))
        if self.NAMES[0] == 'msvc' and self.version_number < (7,):
            raise waflib.Errors.WafError('unsupported compiler')
        env.NO_MSVC_DETECT = 1
        env.INCLUDES = self.includes
        env.LIBPATH = self.libdirs
        env.PATH = self.path + os.environ['PATH'].split(os.pathsep)
        env.MSVC_PATH = self.path
        env.MSVC_COMPILER = self.NAMES[0]
        env.MSVC_VERSION = version_number
        env.MSVC_MANIFEST = 0
        env.MSVC_TARGETS = [self.arch_name]
        env.MSVC_BATFILE = [self.batfile, self.args]
        env.COMPILER_NAME = 'msvc'
        env.COMPILER_TARGET = 'windows-win32-msvc-%s' % version
        configuration_context.load(['msvc'])
        if self.NAMES[0] == 'intel':
            env.append_value('CFLAGS', ['/Qmultibyte-chars-'])
            env.append_value('CXXFLAGS', ['/Qmultibyte-chars-'])
        env.append_unique('LINKFLAGS', ['/MANIFEST:NO'])

    def load_in_env(self,
                    configuration_context: ConfigurationContext,
                    platform: Platform) -> None:
        Compiler.load_in_env(self, configuration_context, platform)
        env = configuration_context.env
        if self.arch == 'amd64':
            configuration_context.find_program('ml64', var='ML', path_list=env.PATH, mandatory=False)
        if self.arch == 'x86':
            configuration_context.find_program('ml', var='ML', path_list=env.PATH, mandatory=False)
        env.SYSTEM_INCLUDE_PATTERN = '/I%s'
        env.IDIRAFTER = '/I'
        if os_platform().endswith('64'):
            configuration_context.find_program('cdb64', var='CDB', mandatory=False)
        else:
            configuration_context.find_program('cdb', var='CDB', mandatory=False)

        env.COMPILER_C_INCLUDES = self.includes
        env.COMPILER_CXX_INCLUDES = self.includes
        main_test = configuration_context.bldnode.make_node('main.c')
        main_test_pp = configuration_context.bldnode.make_node('main.i')
        with open(main_test.abspath(), 'w') as macro_dump_file:
            macro_dump_file.write('#define show(X) #X X\n')
            for macro in MSVC_PREDEFINED_MACROS:
                macro_dump_file.write(
                    '#ifdef %s\n'
                    'show(%s)\n'
                    '#endif\n' % (macro, macro)
                )
        macros_c = []
        self.run_c(['/TC', '/EP', '/P', '/Fi:%s' % main_test_pp.abspath(), main_test.abspath(), ])
        with open(main_test_pp.abspath(), 'r') as listing:
            for line in listing.readlines():
                line = line.strip()
                if line:
                    _, macro, value = line.split('"', maxsplit=2)
                    value = value.strip()
                    macros_c.append('%s=%s' % (macro, value))
        env.COMPILER_C_DEFINES = macros_c
        macros_cxx = []
        self.run_c(
            ['/TP', '/std:c++14', '/Zc:__cplusplus', '/EP', '/P', '/Fi:%s' % main_test_pp.abspath(),
             main_test.abspath(), ])
        with open(main_test_pp.abspath(), 'r') as listing:
            for line in listing.readlines():
                line = line.strip()
                if line:
                    _, macro, value = line.split('"', maxsplit=2)
                    value = value.strip()
                    macros_cxx.append('%s=%s' % (macro, value))
        env.COMPILER_CXX_DEFINES = macros_cxx
        main_test.delete(evict=True)
        main_test_pp.delete(evict=True)
        env.CXXFLAGS_cxx98 = []
        env.CXXFLAGS_cxx03 = []
        env.CXXFLAGS_cxx11 = []
        env.CXXFLAGS_cxx14 = ['/std:c++14']
        env.CXXFLAGS_cxx17 = ['/std:c++17']
        env.CXXFLAGS_cxx20 = ['/std:c++20']
        env.CXXFLAGS_cxx23 = ['/std:c++latest']


all_icl_platforms = (
    ('intel64', 'intel64', 'amd64'),
    ('em64t', 'em64t', 'amd64'),
    ('em64t_native', 'intel64', 'amd64'),
    ('ia32e', 'ia32e', 'amd64'),
    ('ia32', 'ia32', 'x86'),
    ('itanium', 'itanium', 'ia64'),
    ('ia64', 'ia64', 'ia64'),
)

_MsvcVersion = Tuple[str, str, str, str, List[str], List[str], List[str]]
_MsvcVersionDict = Dict[str, Dict[str, waflib.Tools.msvc.target_compiler]]


def gather_vswhere_versions(configuration_context: ConfigurationContext,
                            versions: _MsvcVersionDict) -> None:
    import json
    prg_path = os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles', 'C:\\Program Files (x86)'))

    vswhere = os.path.join(prg_path, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    args = [
        vswhere, '-prerelease', '-products', '*', '-requires', 'Microsoft.VisualStudio.Workload.NativeDesktop',
        '-requires', 'Microsoft.VisualStudio.Workload.VCTools', '-requiresAny', '-format', 'json'
    ]
    try:
        txt = configuration_context.cmd_and_log(args)
    except waflib.Errors.WafError as e:
        waflib.Logs.debug('msvc: vswhere.exe failed %s' % e)
        return

    assert isinstance(txt, str)
    arr = json.loads(txt)
    arr.sort(key=lambda x: x['installationVersion'])
    for entry in arr:
        product = entry['productId'].split('.')[-1].lower()
        ver = entry['installationVersion']
        ver = str('.'.join(ver.split('.')[:2]))
        path = str(os.path.abspath(entry['installationPath']))
        if os.path.exists(path) and ('%s %s' % (product, ver)) not in versions:
            waflib.Tools.msvc.gather_msvc_targets(configuration_context, versions, ver, path, product)


def gather_intel_composer_versions(configuration_context: ConfigurationContext,
                                   versions: _MsvcVersionDict) -> None:
    if sys.platform == "win32":
        import winreg

        version_pattern_suite = re.compile(r'^...?.?\..?.?')
        try:
            all_versions = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                          r'SOFTWARE\Wow6432node\Intel\Suites')
        except OSError:
            try:
                all_versions = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Intel\Suites')
            except OSError:
                return
        index = 0
        while 1:
            try:
                version = winreg.EnumKey(all_versions, index)
            except OSError:
                break
            index += 1
            if version_pattern_suite.match(version):
                version_str = '%s.%s' % (version[0:2], version[3])
            else:
                continue
            all_minor_versions = winreg.OpenKey(all_versions, version)
            minor_index = 0
            while 1:
                try:
                    minor_version = winreg.EnumKey(all_minor_versions, minor_index)
                except OSError:
                    break
                else:
                    minor_index += 1
                    targets = {}
                    for target, target_arg, arch in all_icl_platforms:
                        try:
                            # check if target is installed
                            winreg.OpenKey(all_minor_versions, '%s\\C++\\%s' % (minor_version, target))
                            # retrieve ProductDir
                            icl_version = winreg.OpenKey(all_minor_versions, '%s\\C++' % minor_version)
                            path, _ = winreg.QueryValueEx(icl_version, 'ProductDir')
                        except OSError:
                            continue
                        else:
                            batch_file = os.path.join(path, 'bin', 'iclvars.bat')
                            if os.path.isfile(batch_file):
                                targets[target_arg] = waflib.Tools.msvc.target_compiler(
                                    configuration_context, 'intel', arch, version_str, target_arg, batch_file
                                )
                    versions['intel ' + version_str] = targets


def gather_vstudio_compilers(configuration_context: ConfigurationContext) -> List[_MsvcVersion]:
    try:
        import json
    except ImportError:
        waflib.Logs.error('Visual Studio 2017+ detection requires JSon')
        return []

    prg_path = os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles', 'C:\\Program Files (x86)'))

    vswhere = os.path.join(prg_path, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    args = [vswhere, '-requires', 'Microsoft.VisualStudio.Workload.NativeDesktop', '-format', 'json']
    try:
        txt = configuration_context.cmd_and_log(args)
    except waflib.Errors.WafError:
        return []
    else:
        result = []
        assert isinstance(txt, str)
        instances = json.loads(txt)
        compilers = {}
        for instance in instances:
            installation_path = instance['installationPath']
            toolsets = os.listdir(os.path.join(installation_path, 'VC/Tools/MSVC'))
            for toolset in toolsets:
                hosts = os.listdir(os.path.join(installation_path, 'VC/Tools/MSVC', toolset, 'bin'))
                for host in hosts:
                    if host.startswith('Host'):
                        host_arch = host[4:].lower()
                        targets = os.listdir(os.path.join(installation_path, 'VC/Tools/MSVC', toolset, 'bin', host))
                        version = tuple(int(i) for i in toolset.split('.'))
                        toolset_short = '%d.%d' % (version[0], version[1])
                        for target in targets:
                            if (toolset_short, host_arch, target) not in compilers:
                                compilers[toolset_short, host_arch, target] = (
                                    version, installation_path, toolset_short, host_arch, target)
                            elif compilers[toolset_short, host_arch, target][0] < version:
                                compilers[toolset_short, host_arch, target] = (
                                    version, installation_path, toolset_short, host_arch, target)
        for version, installationPath, toolset_short, host_arch, target in sorted(compilers.values()):
            result.append(
                get_msvc_version_new(configuration_context, installationPath, toolset_short, host_arch, target))
        return result


_msvc_cnt = 0


def get_msvc_version_new(
        configuration_context: ConfigurationContext,
        install_dir: str,
        version: str,
        host: str,
        target: str
) -> _MsvcVersion:
    global _msvc_cnt
    _msvc_cnt += 1
    batfile = configuration_context.bldnode.make_node('waf-print-msvc-%d.bat' % _msvc_cnt)
    batfile.write("""@echo off
set INCLUDE=
set LIB=
call "%s\\Common7\\Tools\\vsdevcmd.bat" -arch=%s -host_arch=%s -vcvars_ver=%s -no_logo
echo PATH=%%PATH%%
echo INCLUDE=%%INCLUDE%%
echo LIB=%%LIB%%;%%LIBPATH%%
""" % (install_dir, target, host, version))
    sout = configuration_context.cmd_and_log(['cmd.exe', '/E:on', '/V:on', '/C', batfile.abspath()])
    assert isinstance(sout, str)
    lines = sout.splitlines()

    if not lines[0]:
        lines.pop(0)
    existing_paths = os.environ['PATH'].split(';')

    path = ''
    msvc_path = msvc_incdir = msvc_libdir = []  # type: List[str]
    for line in lines:
        if line.startswith('PATH='):
            path = line[5:]
            msvc_path = [p for p in path.split(';') if p not in existing_paths]
        elif line.startswith('INCLUDE='):
            msvc_incdir = [i for i in line[8:].split(';') if i]
        elif line.startswith('LIB='):
            msvc_libdir = [i for i in line[4:].split(';') if i]
    if None in (msvc_path, msvc_incdir, msvc_libdir):
        configuration_context.fatal('msvc: Could not find a valid architecture for building (get_msvc_version_new)')

    # Check if the compiler is usable at all.
    # The detection may return 64-bit versions even on 32-bit systems, and these would fail to run.
    env = dict(os.environ)
    if path:
        env.update(PATH=path)
    try:
        cxx = configuration_context.find_program('cl', path_list=msvc_path)
    except waflib.Errors.WafError:
        configuration_context.fatal('msvc: Could not find a valid architecture for building (get_msvc_version_new)')
    else:
        # delete CL if exists. because it could contain parameters which can change cl's behaviour
        if 'CL' in env:
            del (env['CL'])
        assert cxx is not None
        try:
            configuration_context.cmd_and_log(cxx + ['/help'], env=env)
        except UnicodeError:
            configuration_context.fatal('msvc: Unicode error - check the code page?')
        except OSError:
            configuration_context.fatal(
                'msvc: cannot run the compiler in get_msvc_version (run with -v to display errors)')
        finally:
            configuration_context.env['cl'] = ''
    return (
        os.path.join(install_dir, 'Common7\\Tools\\vsdevcmd.bat'),
        version,
        host,
        target,
        msvc_path,
        msvc_incdir,
        msvc_libdir
    )


@waflib.Configure.conf
def get_msvc_versions(configuration_context: waflib.Context.Context) -> _MsvcVersionDict:
    dct = {}  # type: _MsvcVersionDict
    assert isinstance(configuration_context, ConfigurationContext)
    gather_intel_composer_versions(configuration_context, dct)
    waflib.Logs.debug('msvc: detected versions %r' % list(dct.keys()))
    return dct


def os_platform() -> str:
    true_platform = os.environ['PROCESSOR_ARCHITECTURE']
    try:
        true_platform = os.environ["PROCESSOR_ARCHITEW6432"]
    except KeyError:
        pass
        # true_platform not assigned to if this does not exist
    return true_platform


def configure_compiler_msvc(configuration_context: ConfigurationContext) -> List[MSVC]:
    seen = set()  # type: Set[Union[str, Tuple[str, str]]]
    result = []
    configuration_context.start_msg('Looking for msvc compilers')
    try:
        versions = get_msvc_versions(configuration_context)
    except waflib.Errors.WafError:
        pass
    else:
        for version, targets in sorted(versions.items()):
            name, version = version.split()
            for target_name, target_compiler in sorted(targets.items()):
                target_compiler.evaluate()
                if target_compiler.is_valid:
                    cl = detect_executable(configuration_context, name == 'intel' and 'icl' or 'cl',
                                           target_compiler.bindirs)
                    assert cl is not None
                    c = MSVC(
                        cl, name, version, target_name, target_compiler.cpu, target_compiler.bat,
                        target_compiler.bat_target, target_compiler.bindirs, target_compiler.incdirs,
                        target_compiler.libdirs
                    )
                    if c.name() in seen:
                        continue
                    seen.add(c.name())
                    result.append(c)

    compilers = gather_vstudio_compilers(configuration_context)
    for batfile, version, host_arch, target_arch, path, incdir, libdir in compilers:
        if (version, target_arch) in seen:
            continue
        cl = detect_executable(configuration_context, 'cl', path)
        assert cl is not None
        c = MSVC(
            cl, 'msvc', version, target_arch, target_arch, batfile,
            "-arch=%s -host_arch=%s -vcvars_ver=%s -no_logo" % (target_arch, host_arch, version),
            path, incdir, libdir
        )
        if c.name() in seen:
            continue
        seen.add(c.name())
        seen.add((version, target_arch))
        result.append(c)

    configuration_context.end_msg('done')
    return result
