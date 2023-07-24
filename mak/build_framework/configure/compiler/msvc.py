from waflib import Configure, Utils, Errors, Logs
from waflib.Configure import conf
from waflib.Tools import msvc
import os
import re
import sys

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


class MSVC(Configure.ConfigurationContext.Compiler):

    def __init__(self, cl, name, version, target_arch, arch, bat, args, path, includes, libdirs):
        self.NAMES = [name, 'msvc']
        flags = ['/I%s' % i for i in includes] + ['/LIBPATH:%i' for l in libdirs]
        Configure.ConfigurationContext.Compiler.__init__(
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

    def set_optimisation_options(self, conf):
        conf.env.append_unique('CFLAGS_debug', ['/Od', '/Ob1', '/MDd', '/D_DEBUG', '/GR'])
        conf.env.append_unique('CFLAGS_debug_rtc', ['/RTC1', '/RTCc', '/D_ALLOW_RTCc_IN_STL=1'])
        conf.env.append_unique('CXXFLAGS_debug', ['/Od', '/Ob1', '/MDd', '/D_DEBUG', '/GR', '/EHsc'])
        conf.env.append_unique('CXXFLAGS_debug_rtc', ['/RTC1', '/RTCc', '/D_ALLOW_RTCc_IN_STL=1'])
        conf.env.append_unique('CFLAGS', ['/DEBUG', '/Z7'])
        conf.env.append_unique('CXXFLAGS', ['/DEBUG', '/Z7'])
        conf.env.append_unique('LINKFLAGS', ['/DEBUG', '/INCREMENTAL:no'])

        conf.env.append_unique('CFLAGS_profile', ['/DNDEBUG', '/MD', '/O2', '/Oy-', '/GT', '/GF', '/Gy', '/GR-'])
        conf.env.append_unique(
            'CXXFLAGS_profile', ['/DNDEBUG', '/D_HAS_EXCEPTIONS=0', '/MD', '/O2', '/Oy-', '/GT', '/GF', '/Gy', '/GR-']
        )
        conf.env.append_unique('LINKFLAGS_profile', ['/INCREMENTAL:no'])
        conf.env.append_unique('ARFLAGS_profile', [])

        conf.env.append_unique('CFLAGS_final', ['/DNDEBUG', '/MD', '/O2', '/GT', '/GF', '/Gy', '/GR-'])
        conf.env.append_unique(
            'CXXFLAGS_final', ['/DNDEBUG', '/D_HAS_EXCEPTIONS=0', '/MD', '/O2', '/GT', '/GF', '/Gy', '/GR-']
        )
        conf.env.append_unique('LINKFLAGS_final', ['/INCREMENTAL:no'])
        conf.env.append_unique('ARFLAGS_final', [])

        if self.arch == 'x86':
            conf.env.append_unique('CFLAGS', ['/arch:SSE2'])
            conf.env.append_unique('CXXFLAGS', ['/arch:SSE2'])
        if self.NAMES[0] != 'msvc' or self.version_number >= (8,):
            conf.env.append_unique('CFLAGS_profile', ['/GS-'])
            conf.env.append_unique('CXXFLAGS_profile', ['/GS-'])
            conf.env.append_unique('CFLAGS_final', ['/GS-'])
            conf.env.append_unique('CXXFLAGS_final', ['/GS-'])
        if self.NAMES[0] != 'intel' or self.version_number >= (9, 1):
            conf.env.append_unique('CXXFLAGS_cxxstlib', ['/Zl'])
            conf.env.append_unique('CFLAGS_cxxstlib', ['/Zl'])

    def set_warning_options(self, conf):
        if self.NAMES[0] == 'intel':
            conf.env.append_unique('CXXFLAGS', ['/Zc:forScope'])
            if self.version_number >= (11,):
                warning = ['/W4', '/Qdiag-disable:remark']
            else:
                warning = ['/W3']
        else:
            warning = ['/W4']
        conf.env.append_unique('CFLAGS_warnall', warning + ['/D_CRT_SECURE_NO_WARNINGS=1'])
        conf.env.append_unique('CFLAGS_warnnone', ['/D_CRT_SECURE_NO_WARNINGS=1', '/W0'])
        conf.env.append_unique('CFLAGS_werror', ['/WX'])
        conf.env.append_unique('CXXFLAGS_warnall', warning + ['/D_CRT_SECURE_NO_WARNINGS=1'])
        conf.env.append_unique('CXXFLAGS_warnnone', ['/D_CRT_SECURE_NO_WARNINGS=1', '/W0'])
        conf.env.append_unique('CXXFLAGS_werror', ['/WX'])
        if self.NAMES[0] == 'msvc' and self.version_number >= (14,):
            conf.env.append_unique('CFLAGS_warnall', ['/D_ALLOW_RTCc_IN_STL=1'])
            conf.env.append_unique('CXXFLAGS_warnall', ['/D_ALLOW_RTCc_IN_STL=1'])
            conf.env.append_unique('CFLAGS_warnnone', ['/D_ALLOW_RTCc_IN_STL=1'])
            conf.env.append_unique('CXXFLAGS_warnnone', ['/D_ALLOW_RTCc_IN_STL=1'])

    def load_tools(self, conf, platform):
        env = conf.env
        version = '%s %s' % (self.NAMES[0], self.version)
        version_number = tuple(int(i) for i in self.version.split('.'))
        if self.NAMES[0] == 'msvc' and self.version_number < (7,):
            raise Errors.WafError('unsupported compiler')
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
        conf.load('msvc')
        if self.NAMES[0] == 'intel':
            env.append_value('CFLAGS', ['/Qmultibyte-chars-'])
            env.append_value('CXXFLAGS', ['/Qmultibyte-chars-'])
        env.append_unique('LINKFLAGS', ['/MANIFEST:NO'])

    def load_in_env(self, conf, platform):
        Configure.ConfigurationContext.Compiler.load_in_env(self, conf, platform)
        if self.arch == 'amd64':
            conf.find_program('ml64', var='ML', path_list=conf.env.PATH, mandatory=False)
        if self.arch == 'x86':
            conf.find_program('ml', var='ML', path_list=conf.env.PATH, mandatory=False)
        env = conf.env
        env.SYSTEM_INCLUDE_PATTERN = '/I%s'
        env.IDIRAFTER = '/I'
        if os_platform().endswith('64'):
            conf.find_program('cdb64', var='CDB', mandatory=False)
        else:
            conf.find_program('cdb', var='CDB', mandatory=False)

        env.COMPILER_C_INCLUDES = self.includes
        env.COMPILER_CXX_INCLUDES = self.includes
        main_test = conf.bldnode.make_node('main.c')
        main_test_pp = conf.bldnode.make_node('main.i')
        with open(main_test.abspath(), 'w') as macro_dump_file:
            macro_dump_file.write('#define show(X) #X X\n')
            for macro in MSVC_PREDEFINED_MACROS:
                macro_dump_file.write(
                    '#ifdef %s\n'
                    'show(%s)\n'
                    '#endif\n' % (macro, macro)
                )
        macros_c = []
        result, out, err = self.run_c(['/TC', '/EP', '/P', '/Fi:%s' % main_test_pp.abspath(), main_test.abspath(), ])
        with open(main_test_pp.abspath(), 'r') as listing:
            for line in listing.readlines():
                line = line.strip()
                if line:
                    _, macro, value = line.split('"', maxsplit=2)
                    value = value.strip()
                    macros_c.append('%s=%s' % (macro, value))
        env.COMPILER_C_DEFINES = macros_c
        macros_cxx = []
        result, out, err = self.run_c(
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


@conf
def gather_vswhere_versions(conf, versions):
    import json
    prg_path = os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles', 'C:\\Program Files (x86)'))

    vswhere = os.path.join(prg_path, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    args = [
        vswhere, '-prerelease', '-products', '*', '-requires', 'Microsoft.VisualStudio.Workload.NativeDesktop',
        '-requires', 'Microsoft.VisualStudio.Workload.VCTools', '-requiresAny', '-format', 'json'
    ]
    try:
        txt = conf.cmd_and_log(args)
    except Errors.WafError as e:
        Logs.debug('msvc: vswhere.exe failed %s', e)
        return

    if sys.version_info[0] < 3:
        try:
            txt = txt.decode(sys.stdout.encoding or 'cp1252')
        except UnicodeError:
            txt = txt.decode('utf-8', 'replace')
    arr = json.loads(txt)
    arr.sort(key=lambda x: x['installationVersion'])
    for entry in arr:
        product = entry['productId'].split('.')[-1].lower()
        ver = entry['installationVersion']
        ver = str('.'.join(ver.split('.')[:2]))
        path = str(os.path.abspath(entry['installationPath']))
        if os.path.exists(path) and ('%s %s' % (product, ver)) not in versions:
            conf.gather_msvc_targets(versions, ver, path, product)


@conf
def gather_intel_composer_versions(conf, versions):
    version_pattern_suite = re.compile('^...?.?\..?.?')
    try:
        all_versions = Utils.winreg.OpenKey(Utils.winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432node\Intel\Suites')
    except OSError:
        try:
            all_versions = Utils.winreg.OpenKey(Utils.winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Intel\Suites')
        except OSError:
            return
    index = 0
    while 1:
        try:
            version = Utils.winreg.EnumKey(all_versions, index)
        except OSError:
            break
        index += 1
        if version_pattern_suite.match(version):
            version_str = '%s.%s' % (version[0:2], version[3])
        else:
            continue
        all_minor_versions = Utils.winreg.OpenKey(all_versions, version)
        minor_index = 0
        while 1:
            try:
                minor_version = Utils.winreg.EnumKey(all_minor_versions, minor_index)
            except OSError:
                break
            else:
                minor_index += 1
                targets = {}
                for target, target_arg, arch in all_icl_platforms:
                    try:
                        # check if target is installed
                        Utils.winreg.OpenKey(all_minor_versions, '%s\\C++\\%s' % (minor_version, target))
                        # retrieve ProductDir
                        icl_version = Utils.winreg.OpenKey(all_minor_versions, '%s\\C++' % minor_version)
                        path, type = Utils.winreg.QueryValueEx(icl_version, 'ProductDir')
                    except OSError:
                        continue
                    else:
                        batch_file = os.path.join(path, 'bin', 'iclvars.bat')
                        if os.path.isfile(batch_file):
                            targets[target_arg] = msvc.target_compiler(
                                conf, 'intel', arch, version_str, target_arg, batch_file
                            )
                versions['intel ' + version_str] = targets


@conf
def gather_vstudio_compilers(conf):
    try:
        import json
    except ImportError:
        Logs.error('Visual Studio 2017+ detection requires JSon')
        return []

    prg_path = os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles', 'C:\\Program Files (x86)'))

    vswhere = os.path.join(prg_path, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    args = [vswhere, '-requires', 'Microsoft.VisualStudio.Workload.NativeDesktop', '-format', 'json']
    try:
        txt = conf.cmd_and_log(args)
    except Errors.WafError as e:
        return []
    else:
        result = []
        instances = json.loads(txt)
        compilers = {}
        for instance in instances:
            installationPath = instance['installationPath']
            toolsets = os.listdir(os.path.join(installationPath, 'VC/Tools/MSVC'))
            for toolset in toolsets:
                hosts = os.listdir(os.path.join(installationPath, 'VC/Tools/MSVC', toolset, 'bin'))
                for host in hosts:
                    if host.startswith('Host'):
                        host_arch = host[4:].lower()
                        targets = os.listdir(os.path.join(installationPath, 'VC/Tools/MSVC', toolset, 'bin', host))
                        version = tuple(int(i) for i in toolset.split('.'))
                        toolset_short = '%d.%d' % (version[0], version[1])
                        for target in targets:
                            if (toolset_short, host_arch, target) not in compilers:
                                compilers[toolset_short, host_arch, target] = (
                                    version, installationPath, toolset_short, host_arch, target)
                            elif compilers[toolset_short, host_arch, target][0] < version:
                                compilers[toolset_short, host_arch, target] = (
                                    version, installationPath, toolset_short, host_arch, target)
        for version, installationPath, toolset_short, host_arch, target in sorted(compilers.values()):
            result.append(conf.get_msvc_version_new(installationPath, toolset_short, host_arch, target))
        return result


@conf
def get_msvc_version_new(conf, install_dir, version, host, target):
    """
    Checks that an installed compiler actually runs and uses vcvars to obtain the
    environment needed by the compiler.

    :param install_dir: Visual Studio installation directory.
    :param version: Compiler version to discover
    :param target: target architecture
    :return: the location of the compiler executable, the location of include dirs, and the library paths
    :rtype: tuple of strings
    """
    try:
        conf.msvc_cnt += 1
    except AttributeError:
        conf.msvc_cnt = 1
    batfile = conf.bldnode.make_node('waf-print-msvc-%d.bat' % conf.msvc_cnt)
    batfile.write("""@echo off
set INCLUDE=
set LIB=
call "%s\\Common7\\Tools\\vsdevcmd.bat" -arch=%s -host_arch=%s -vcvars_ver=%s -no_logo
echo PATH=%%PATH%%
echo INCLUDE=%%INCLUDE%%
echo LIB=%%LIB%%;%%LIBPATH%%
""" % (install_dir, target, host, version))
    sout = conf.cmd_and_log(['cmd.exe', '/E:on', '/V:on', '/C', batfile.abspath()])
    lines = sout.splitlines()

    if not lines[0]:
        lines.pop(0)
    existing_paths = os.environ['PATH'].split(';')

    msvc_path = msvc_incdir = msvc_libdir = None
    for line in lines:
        if line.startswith('PATH='):
            path = line[5:]
            msvc_path = [p for p in path.split(';') if p not in existing_paths]
        elif line.startswith('INCLUDE='):
            msvc_incdir = [i for i in line[8:].split(';') if i]
        elif line.startswith('LIB='):
            msvc_libdir = [i for i in line[4:].split(';') if i]
    if None in (msvc_path, msvc_incdir, msvc_libdir):
        conf.fatal('msvc: Could not find a valid architecture for building (get_msvc_version_new)')

    # Check if the compiler is usable at all.
    # The detection may return 64-bit versions even on 32-bit systems, and these would fail to run.
    env = dict(os.environ)
    env.update(PATH=path)
    try:
        cxx = conf.find_program('cl', path_list=msvc_path)
    except Errors.WafError as e:
        print(e)

    # delete CL if exists. because it could contain parameters which can change cl's behaviour rather catastrophically.
    if 'CL' in env:
        del (env['CL'])
    try:
        conf.cmd_and_log(cxx + ['/help'], env=env)
    except UnicodeError:
        conf.fatal('msvc: Unicode error - check the code page?')
    except Exception:
        conf.fatal('msvc: cannot run the compiler in get_msvc_version (run with -v to display errors)')
    finally:
        conf.env['cl'] = ''

    return os.path.join(install_dir,
                        'Common7\\Tools\\vsdevcmd.bat'), version, host, target, msvc_path, msvc_incdir, msvc_libdir


@conf
def get_msvc_versions(self):
    """
	:return: platform to compiler configurations
	:rtype: dict
	"""
    dct = Utils.ordered_iter_dict()
    self.gather_intel_composer_versions(dct)
    Logs.debug('msvc: detected versions %r', list(dct.keys()))
    return dct


def os_platform():
    true_platform = os.environ['PROCESSOR_ARCHITECTURE']
    try:
        true_platform = os.environ["PROCESSOR_ARCHITEW6432"]
    except KeyError:
        pass
        # true_platform not assigned to if this does not exist
    return true_platform


def configure(conf):
    seen = set([])
    from waflib.Tools import msvc
    conf.start_msg('Looking for msvc compilers')
    try:
        versions = conf.get_msvc_versions()
    except Exception as e:
        pass
    else:
        for version, targets in sorted(versions.items()):
            name, version = version.split()
            for target_name, target_compiler in sorted(targets.items()):
                target_compiler.evaluate()
                if target_compiler.is_valid:
                    cl = conf.detect_executable(name == 'intel' and 'icl' or 'cl', target_compiler.bindirs)
                    c = MSVC(
                        cl, name, version, target_name, target_compiler.cpu, target_compiler.bat,
                        target_compiler.bat_target, target_compiler.bindirs, target_compiler.incdirs,
                        target_compiler.libdirs
                    )
                    if c.name() in seen:
                        continue
                    seen.add(c.name())
                    conf.compilers.append(c)

    compilers = conf.gather_vstudio_compilers()
    for batfile, version, host_arch, target_arch, path, incdir, libdir in compilers:
        if (version, target_arch) in seen:
            continue
        cl = conf.detect_executable('cl', path)
        c = MSVC(
            cl, 'msvc', version, target_arch, target_arch, batfile,
            "-arch=%s -host_arch=%s -vcvars_ver=%s -no_logo" % (target_arch, host_arch, version),
            path, incdir, libdir
        )
        if c.name() in seen:
            continue
        seen.add(c.name())
        seen.add((version, target_arch))
        conf.compilers.append(c)

    conf.end_msg('done')
