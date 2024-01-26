import os
import re
import waflib.Context
import waflib.Errors
import waflib.Options
import macholib.MachO
import plist_smalllib
from ...options import ConfigurationContext
from .platform import Platform
from .compiler import Compiler, detect_executable
from typing import Dict, List, Optional, Tuple


class DarwinSDKInfo(object):
    def __init__(
            self,
            version: List[str],
            archs: List[str],
            path: str
    ) -> None:
        self.version = version
        self.archs = archs
        self.path = path


class DarwinSDK(object):
    def __init__(
            self,
            sdk_version: str,
            sdk_path: str,
            bin_paths: List[str],
            minimum_version: str,
            cflags: List[str],
            cxxflags: List[str],
            ldflags: List[str]
    ) -> None:
        self.sdk_version = sdk_version
        self.sdk_path = sdk_path
        self.bin_paths = bin_paths
        self.minimum_version = minimum_version
        self.cflags = cflags
        self.cxxflags = cxxflags
        self.ldflags = ldflags


class Darwin(Platform):
    NAME = 'Darwin'
    SDK_NAME = 'Darwin'
    OS_NAME = 'darwin'
    SUPPORTED_TARGETS = (re.compile(r'.*-darwin.*'),)
    PLATFORMS = ['darwin']
    SDKS = {}  # type: Dict[str, List[DarwinSDKInfo]]

    def __init__(
            self,
            configuration_context: ConfigurationContext,
            sdk: Optional[DarwinSDK] = None):
        Platform.__init__(self)
        self.sdk = sdk
        self.configuration_context = configuration_context
        if sdk is not None:
            self.NAME = self.__class__.NAME + sdk.sdk_version
            self.directories += sdk.bin_paths

    def platform_name(self, _: Compiler) -> str:
        assert self.sdk is not None
        return self.__class__.NAME.lower() + self.sdk.sdk_version

    def get_available_compilers(
            self,
            configuration_context: ConfigurationContext,
            compiler_list: List[Compiler]
    ) -> List[Tuple[Compiler, List[Compiler], Platform]]:
        result = []  # type: List[Tuple[Compiler, List[Compiler], Platform]]
        compiler_sets = {}  # type: Dict[Tuple[str, str], List[Compiler]]
        for c in compiler_list:
            for r in self.SUPPORTED_TARGETS:
                if r.match(c.target):
                    k = (c.NAMES[0], c.version)
                    try:
                        compiler_sets[k].append(c)
                    except KeyError:
                        compiler_sets[k] = [c]
                    break
        if compiler_sets:
            self.configuration_context.start_msg('Looking for %s SDKs' % self.SDK_NAME)
            for k in sorted(compiler_sets.keys()):
                compilers = compiler_sets[k]
                try:
                    compilers, sdk = self.get_best_compilers_sdk(compilers)
                except waflib.Errors.WafError:
                    continue
                else:
                    if len(compilers) > 1:
                        result.append((compilers[0], compilers, self.__class__(self.configuration_context, sdk)))
                    else:
                        result.append((compilers[0], [], self.__class__(self.configuration_context, sdk)))
            if result:
                self.configuration_context.end_msg('done')
            else:
                self.configuration_context.end_msg('none', color='YELLOW')
        return result

    @staticmethod
    def get_root_dirs(appname: str) -> Tuple[str, str, str, str]:
        return (
            os.path.join(appname + '.app', 'Contents'),
            os.path.join(appname + '.app', 'Contents', 'MacOS'),
            os.path.join(appname + '.app', 'Contents', 'Plugins'),
            os.path.join(appname + '.app', 'Contents', 'Resources'),
        )

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        assert self.sdk is not None
        platform = self.SDK_NAME.lower()
        compiler.find_target_program(configuration_context, self, 'lipo',
                                     mandatory=False)
        if not configuration_context.env.LIPO:
            configuration_context.find_program('lipo')
        compiler.find_target_program(configuration_context, self, 'codesign', mandatory=False)
        if not configuration_context.env.CODESIGN:
            configuration_context.find_program('codesign', mandatory=False)
        compiler.find_target_program(configuration_context, self, 'dsymutil', mandatory=False)
        if not configuration_context.env.DSYMUTIL:
            configuration_context.find_program('dsymutil', mandatory=False)
        if not configuration_context.env.DSYMUTIL:
            compiler.find_target_program(configuration_context, self, 'llvm-dsymutil', var='DSYMUTIL',
                                         mandatory=False)
        if not configuration_context.env.DSYMUTIL:
            configuration_context.find_program('llvm-dsymutil', var='DSYMUTIL', mandatory=False)
        environ = getattr(configuration_context, 'environ', os.environ)
        env = configuration_context.env
        env.PATH = os.path.pathsep.join(self.directories + compiler.directories + [environ['PATH']])
        env.ABI = 'mach_o'
        env.COMPILER_ABI = 'gcc'
        env.VALID_PLATFORMS = self.PLATFORMS + ['darwin']
        env.XCODE_SDKROOT = platform
        env.XCODE_ABI = 'mach_o'
        env.XCODE_SUPPORTEDPLATFORMS = platform
        env.CFLAGS_cshlib = ['-fPIC']
        env.CXXFLAGS_cxxshlib = ['-fPIC']
        env.LINKFLAGS_cshlib = ['-dynamiclib']
        env.LINKFLAGS_cxxshlib = ['-dynamiclib']
        env.cshlib_PATTERN = 'lib%s.dylib'
        env.cxxshlib_PATTERN = 'lib%s.dylib'
        env.FRAMEWORKPATH_ST = '-F%s'
        env.FRAMEWORK_ST = ['-framework']
        env.ARCH_ST = ['-arch']

        env.LINKFLAGS_cxxstlib = []

        env.SHLIB_MARKER = []
        env.STLIB_MARKER = []
        env.SONAME_ST = []
        env.pymodule_PATTERN = '%s.so'

        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, configuration_context.srcnode.name)
        root_dir, bin_dir, runlib_dir, resources_dir = self.get_root_dirs(appname)
        env.DEPLOY_ROOTDIR = root_dir
        env.DEPLOY_BINDIR = bin_dir
        env.DEPLOY_RUNBINDIR = runlib_dir
        env.DEPLOY_LIBDIR = 'lib'
        env.DEPLOY_INCLUDEDIR = 'include'
        env.DEPLOY_DATADIR = resources_dir
        env.DEPLOY_PLUGINDIR = os.path.join(runlib_dir, 'plugins')
        env.DEPLOY_KERNELDIR = os.path.join(runlib_dir, 'kernels')
        env.append_unique('DEFINES', ['_BSD_SOURCE'])

        env.MACOSX_SDK = os.path.splitext(os.path.basename(self.sdk.sdk_path))[0]
        env.XCODE_SDK_PATH = self.sdk.sdk_path
        env.SYSROOT = self.sdk.sdk_path
        env.MACOSX_SDK_MIN = self.sdk.minimum_version
        env.append_unique('CPPFLAGS', ['-isysroot', self.sdk.sdk_path])
        env.append_unique('CFLAGS', ['-isysroot', self.sdk.sdk_path] + self.sdk.cflags)
        env.append_unique('CXXFLAGS', ['-isysroot', self.sdk.sdk_path] + self.sdk.cxxflags)
        env.append_unique(
            'LINKFLAGS',
            ['-isysroot', self.sdk.sdk_path, '-L%s/usr/lib' % self.sdk.sdk_path] + self.sdk.ldflags +
            ['-B%s' % bin_path for bin_path in self.directories]
        )
        env.env = dict(os.environ)

    platform_sdk_re = re.compile(r'.*/Platforms/\w*\.platform/Developer/SDKs/[\.\w]*\.sdk')
    old_sdk_re = re.compile(r'.*/SDKs/[\.\w]*\.sdk')

    def match(self, compiler: Compiler, sdk_path: str, all_sdks: List[DarwinSDKInfo]) -> bool:

        def get_paths(root_path: str) -> Tuple[str, str]:
            if self.platform_sdk_re.match(root_path):
                _platform_path = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(root_path))))
                _developer_path, d = os.path.split(_platform_path)
                while d and not d.startswith('Developer'):
                    _developer_path, d = os.path.split(_developer_path)
            elif self.old_sdk_re.match(root_path):
                _platform_path = os.path.normpath(os.path.dirname(os.path.dirname(root_path)))
                _developer_path, d = os.path.split(_platform_path)
            else:
                _platform_path = os.path.normpath(os.path.dirname(os.path.dirname(root_path)))
                _developer_path, d = os.path.split(_platform_path)
            _developer_path = os.path.join(_developer_path, d)
            if _platform_path[-1] != '/':
                _platform_path += '/'
            if _developer_path[-1] != '/':
                _developer_path += '/'
            return _platform_path, _developer_path

        compiler_path = os.path.normpath(compiler.compiler_c)
        platform_path, developer_path = get_paths(sdk_path)
        if compiler_path.startswith(platform_path):
            return True
        for sdk in all_sdks:
            ppath, dpath = get_paths(sdk.path)
            if compiler_path.startswith(ppath):
                return False
        if compiler_path.startswith(developer_path):
            return True
        for sdk in all_sdks:
            ppath, dpath = get_paths(sdk.path)
            if compiler_path.startswith(dpath):
                return False
        return True

    def get_best_compilers_sdk(self, compilers: List[Compiler]) -> Tuple[List[Compiler], DarwinSDK]:
        src_node = self.configuration_context.bldnode.make_node('test.mm')
        src_node.write(
            '#include <stdio.h>\n'
            '#include <iostream>\n'
            '#include <Foundation/NSObject.h>\n'
            '#include <CoreFoundation/CoreFoundation.h>\n'
            '@interface MotorObject : NSObject {\n'
            '}\n'
            '- (id) init;\n'
            '@end\n'
            '@implementation MotorObject\n'
            '- (id) init {\n'
            ' self = [super init];\n'
            ' return self;\n'
            '}\n'
            '@end\n'
            'int main(int argc, char* argv[])\n'
            '{\n'
            '    [[MotorObject alloc] init];\n'
            '    switch(argc) {\n'
            '    case 6:\n'
            '        return printf("%s\\n", argv[5]);\n'
            '    case 5:\n'
            '        return printf("%s\\n", argv[4]);\n'
            '    case 4:\n'
            '        return printf("%s\\n", argv[3]);\n'
            '    case 3:\n'
            '        return printf("%s\\n", argv[2]);\n'
            '    case 2:\n'
            '        return printf("%s\\n", argv[1]);\n'
            '    default:\n'
            '        return printf("%s\\n", argv[0]);\n'
            '    }\n'
            '}\n'
        )
        obj_node = src_node.change_ext('.o')
        exe_node = src_node.change_ext('')
        all_archs = []
        for compiler in sorted(compilers, key=lambda x: x.name()):
            if compiler.arch not in all_archs:
                all_archs.append(compiler.arch)

        try:
            sdk_number_min = getattr(waflib.Options.options, '%s_sdk_min' % self.OS_NAME)
        except AttributeError:
            sdk_number_min = ''
        sdk_number_min = sdk_number_min and sdk_number_min.split('.') or []
        try:
            sdk_number_max = getattr(waflib.Options.options, '%s_sdk_max' % self.OS_NAME)
        except AttributeError:
            sdk_number_max = ''
        sdk_number_max = sdk_number_max and sdk_number_max.split('.') or []

        try:
            all_sdks = Darwin.SDKS[self.SDK_NAME]
        except KeyError:
            raise waflib.Errors.WafError('No SDK detected for platform %s' % self.SDK_NAME)
        else:
            best_sdk = ([], None)  # type: Tuple[List[Compiler], Optional[DarwinSDK]]
            for sdk in all_sdks:
                if len(best_sdk[0]) >= len(sdk.archs):
                    break
                os_version_min = getattr(self, 'OS_VERSION_MIN', sdk.version)
                os_version_min_libcpp = getattr(self, 'OS_VERSION_MIN_LIBCPP', sdk.version)
                sdk_option = '-m%s-version-min=%s' % (self.OS_NAME, '.'.join(os_version_min))
                if sdk_number_max and sdk.version > sdk_number_max:
                    continue
                if sdk_number_min and sdk.version < sdk_number_min:
                    continue
                sdk_compilers = []
                sdk_bin_paths = [
                    i for i in [
                        os.path.normpath(os.path.join(sdk.path, 'usr', 'bin')),
                        os.path.normpath(os.path.join(sdk.path, '..', '..', 'usr', 'bin')),
                        os.path.normpath(os.path.join(sdk.path, '..', '..', '..', '..', '..', 'usr', 'bin')),
                        os.path.normpath(
                            os.path.join(
                                sdk.path, '..', '..', '..', '..', '..', 'Toolchains', 'XcodeDefault.xctoolchain',
                                'usr',
                                'bin'
                            )
                        ),
                    ] if os.path.isdir(i) and i != '/usr/bin'
                ]
                strip = detect_executable(self.configuration_context, 'strip', path_list=sdk_bin_paths)
                if strip is None:
                    otool = detect_executable(self.configuration_context, 'otool', path_list=sdk_bin_paths)
                    if otool is None:
                        otool = detect_executable(self.configuration_context, 'otool')
                    if otool is not None:
                        strip = detect_executable(self.configuration_context, 'strip',
                                                  path_list=[os.path.dirname(otool)])
                assert strip is not None

                sdk_option = '-m%s-version-min=%s' % (self.OS_NAME, '.'.join(os_version_min_libcpp))
                cflags = [sdk_option]
                cxxflags = ['-stdlib=libc++', sdk_option]
                ldflags = ['-stdlib=libc++', sdk_option]

                for a in sdk.archs:
                    for c in compilers:
                        if self.match(c, sdk.path, all_sdks) and c.arch == c.ARCHS[a]:
                            try:
                                obj_node.delete()
                            except (OSError, KeyError):
                                pass
                            try:
                                exe_node.delete()
                            except (OSError, KeyError):
                                pass
                            env = dict(os.environ)
                            env['PATH'] = os.path.pathsep.join(sdk_bin_paths + c.directories + [env['PATH']])
                            r, out, err = c.run_cxx(
                                [
                                    sdk_option, '-g', '-O2', '-c', '-o',
                                    obj_node.abspath(), '-isysroot', sdk.path,
                                    src_node.abspath(),
                                    '-B%s' % os.path.dirname(strip)
                                ] + cxxflags,
                                env=env
                            )
                            if r == 0:
                                r, out, err = c.run([strip, '-S', obj_node.abspath()], env=env)
                                if r == 0:
                                    r, out, err = c.run_cxx(
                                        [
                                            sdk_option, '-framework', 'Foundation', '-framework', 'CoreFoundation',
                                            '-o',
                                            exe_node.abspath(),
                                            '-L%s' % os.path.join(sdk.path, 'usr', 'lib'), '-isysroot', sdk.path,
                                            obj_node.abspath(), '-lobjc',
                                            '-B%s' % os.path.dirname(strip), '-Wl,-rpath,rpath_test'
                                        ] + cxxflags,
                                        env=env
                                    )
                                    if r == 0:
                                        r, out, err = c.run([strip, '-S', exe_node.abspath()], env=env)
                                        if r == 0:
                                            sdk_compilers.append(c)
                                            break
                if len(sdk_compilers) > len(best_sdk[0]):
                    best_sdk = (sdk_compilers,
                                DarwinSDK('.'.join(sdk.version), sdk.path, [os.path.dirname(strip)] + sdk_bin_paths,
                                          '.'.join(os_version_min), cflags, cxxflags, ldflags))
            if best_sdk[1] is not None:
                return best_sdk[0], best_sdk[1]
            else:
                raise waflib.Errors.WafError('No SDK for compiler %s' % compilers[0].compiler_c)


class MacOS(Darwin):
    NAME = 'MacOS'
    CERTIFICATE_NAME = 'Mac Developer'
    PLATFORMS = ['macos', 'macosx', 'pc', 'darwin']
    SDK_NAME = 'macosx'
    OS_NAME = 'macosx'
    OS_VERSION_MIN = ('10', '5')
    OS_VERSION_MIN_LIBCPP = ('10', '7')

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: Compiler) -> None:
        Darwin.load_in_env(self, configuration_context, compiler)
        assert self.sdk is not None
        sdk_path = self.sdk.sdk_path
        configuration_context.env.SYSTEM_NAME = 'apple-macosx'
        if os.path.isfile(os.path.join(sdk_path, 'usr', 'lib', 'libgcc_s.10.5.dylib')):
            configuration_context.env.append_unique('LINKFLAGS', ['-lgcc_s.10.5'])


def _parse_sdk_settings(sdk_settings_path: str) -> Tuple[str, List[str]]:
    with open(sdk_settings_path, 'rb') as sdk_settings_file:
        settings = plist_smalllib.load(sdk_settings_file)
    assert isinstance(settings, dict)
    default_properties = settings['DefaultProperties']
    assert isinstance(default_properties, dict)
    sdk_name = default_properties['PLATFORM_NAME']
    sdk_version = settings['Version']
    assert isinstance(sdk_version, str)
    return str(sdk_name), [str(x) for x in sdk_version.split('.')]


_CPU_ARCH_ABI64 = 0x01000000

_CPU_TYPE_NAMES = {
    -1: "any",
    # 1: "vax",
    # 6: "mc680x0",
    # 7: "x86",
    _CPU_ARCH_ABI64 | 7: "x86_64",
    # 8: "mips",
    # 10: "mc98000",
    # 11: "hppa",
    # 12: "arm",
    _CPU_ARCH_ABI64 | 12: "arm64",
    # 13: "mc88000",
    # 14: "sparc",
    # 15: "i860",
    # 16: "alpha",
    # 18: "ppc",
    _CPU_ARCH_ABI64 | 18: "ppc64",
}

_CPU_SUBTYPE_NAMES = {
    'arm':
        {
            5: 'v4t',
            6: 'v6',
            7: 'v5tej',
            8: 'xscale',
            9: 'v7',
            10: 'v7f',
            11: 'v7s',
            12: 'v7k',
            13: 'v8',
            14: 'v6m',
            15: 'v7m',
            16: 'v7em',
        },
    'arm64':
        {
            1: 'v8'
        },
}


def configure_target_macos(
        configuration_context: ConfigurationContext,
        platform_list: List[Platform]
) -> None:
    archs = {
        'ppc': 'ppc',
        'ppc_7400': 'ppc',
        'ppc64': 'ppc64',
        'x86_64': 'amd64',
        'i386': 'x86',
        'arm_v6': 'armv6',
        'armv7': 'armv7a',
        'arm_v7': 'armv7a',
        'armv7s': 'armv7s',
        'arm_v7s': 'armv7s',
        'armv7k': 'armv7k',
        'arm_v7k': 'armv7k',
        'arm64': 'arm64',
        'arm64e': 'arm64e',
        'arm64_32': 'arm64_32',
    }

    Darwin.SDKS = {}
    sdks = []
    for p in configuration_context.env.OS_SDK_PATH:
        for sdk in os.listdir(p):
            sdk_path = os.path.join(p, sdk)
            if os.path.isfile(os.path.join(p, sdk, 'SDKSettings.plist')):
                sdks.append(sdk_path)
    for sysroot, _ in configuration_context.env.SYSROOTS:
        if os.path.isfile(os.path.join(sysroot, 'SDKSettings.plist')):
            sdks.append(sysroot)

    for sdk_path in sdks:
        sdk_os, sdk_version = _parse_sdk_settings(os.path.join(sdk_path, 'SDKSettings.plist'))
        sdk_archs = []
        dylib = os.path.join(sdk_path, 'usr', 'lib', 'libc.dylib')
        if os.path.isfile(dylib):
            mach_o = macholib.MachO.MachO(dylib)
            for header in mach_o.headers:
                arch_name = _CPU_TYPE_NAMES.get(header.header.cputype, 'unknown')
                arch_name += _CPU_SUBTYPE_NAMES.get(arch_name, {}).get(header.header.cpusubtype, '')
                sdk_archs.append(arch_name)
        else:
            tbd = os.path.join(sdk_path, 'usr', 'lib', 'libc.tbd')
            if os.path.isfile(tbd):
                with open(tbd, 'r') as tbd_file:
                    for line in tbd_file.readlines():
                        line = line.strip()
                        if line.startswith('archs:'):
                            for a in line.split()[2:-1]:
                                try:
                                    sdk_archs.append(archs[a.split(',')[0]])
                                except KeyError:
                                    print('Unknown %s arch: %s in %s' % (sdk_os, a, dylib))
                            break
                        elif line.startswith('targets:'):
                            for t in line.split()[2:-1]:
                                try:
                                    arch = archs[t.split('-')[0]]
                                except KeyError:
                                    print('Unknown %s target: %s in %s' % (sdk_os, t, dylib))
                                else:
                                    if arch not in sdk_archs:
                                        sdk_archs.append(arch)
                            break
        try:
            Darwin.SDKS[sdk_os].append(DarwinSDKInfo(sdk_version, sdk_archs, sdk_path))
        except KeyError:
            Darwin.SDKS[sdk_os] = [DarwinSDKInfo(sdk_version, sdk_archs, sdk_path)]

    for sdk_os in Darwin.SDKS.keys():
        Darwin.SDKS[sdk_os] = sorted(Darwin.SDKS[sdk_os],
                                     key=lambda sdk_info: (-len(sdk_info.archs), sdk_info.version))

    platform_list.append(MacOS(configuration_context))
