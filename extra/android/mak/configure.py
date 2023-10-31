#! /usr/bin/env python
# set Android specific options

import os
import re
from copy import deepcopy
import build_framework
from build_framework.configure.target import Platform as _Platform
from build_framework.configure.target.compiler import Compiler as _Compiler
from build_framework.configure.target.compiler.clang import Clang as _Clang
import waflib.Context
import waflib.Errors
import waflib.Logs
import waflib.Options
from typing import Dict, List, Optional, Tuple, Union


def _get_android_arch(arch: str) -> str:
    archs = {'armv7a': 'arm', 'amd64': 'x86_64', 'i686': 'x86', 'aarch64': 'arm64'}
    return archs.get(arch, arch)


def _tryint(s: str) -> Union[int, str]:
    try:
        return int(s)
    except ValueError:
        return s


def _alphanum_key(s: str) -> List[Union[int, str]]:
    return [_tryint(c) for c in re.split('([0-9]+)', s)]


def _valid_archs(platform_ndk: str, platform: str, archs: List[str]) -> List[str]:
    result = []
    for arch in archs:
        a = _get_android_arch(arch)
        p = os.path.join(platform_ndk, platform, 'arch-%s' % a)
        if os.path.isdir(p):
            result.append(arch)
    return result


class NdkConfig(object):

    def __init__(self, ndkroot: str, sysroot: str, ldsysroot: str, libpath: List[str], defines: List[str]) -> None:
        self._ndkroot = ndkroot
        self._sysroot = sysroot
        self._ldsysroot = ldsysroot
        self._libpath = libpath
        self._defines = defines

    def get_defines(self) -> List[str]:
        return self._defines

    def get_ndkroot(self) -> str:
        return self._ndkroot

    def get_sysroot(self) -> str:
        return self._sysroot

    def get_ldsysroot(self) -> str:
        return self._ldsysroot

    def get_libpath(self) -> List[str]:
        return self._libpath


class NdkArchConfig:

    def __init__(self, archs: Dict[str, NdkConfig]) -> None:
        self.archs = archs

    def get_ndk_config(self, arch: str) -> NdkConfig:
        return self.archs[_get_android_arch(arch)]

    def get_valid_archs(self, archs: List[str]) -> List[str]:
        return [arch for arch in archs if _get_android_arch(arch) in self.archs]


class NdkVersionConfig:

    def __init__(self, ndkroot: str) -> None:
        self._versions = {}
        platforms_directory = os.path.join(ndkroot, 'platforms')
        if os.path.isdir(platforms_directory):
            sysroot_dir = os.path.join(ndkroot, 'sysroot')
            unified_headers = os.path.isdir(sysroot_dir)
            for version in os.listdir(platforms_directory):
                if os.path.isdir(os.path.join(platforms_directory, version)):
                    defines = []
                    version_number = int(version.split('-')[1])
                    if unified_headers:
                        defines.append('-D__ANDROID_API__=%d' % version_number)
                    arch_configs = {}
                    for arch in os.listdir(os.path.join(platforms_directory, version)):
                        sysroot_arch_dir = os.path.join(platforms_directory, version, arch)
                        if os.path.isdir(sysroot_arch_dir):
                            arch_name = arch.split('-')[1]
                            if os.path.isdir(os.path.join(sysroot_arch_dir, 'usr', 'lib64')):
                                libdir = os.path.join(sysroot_arch_dir, 'usr', 'lib64')
                            else:
                                libdir = os.path.join(sysroot_arch_dir, 'usr', 'lib')
                            arch_configs[arch_name] = NdkConfig(
                                ndkroot, sysroot_dir if unified_headers else sysroot_arch_dir, sysroot_arch_dir,
                                [libdir], defines
                            )
                    self._versions[version_number] = NdkArchConfig(arch_configs)
        else:
            for toolchain in os.listdir(os.path.join(ndkroot, 'toolchains', 'llvm', 'prebuilt')):
                sysroot_dir = os.path.join(ndkroot, 'toolchains', 'llvm', 'prebuilt', toolchain, 'sysroot')
                if os.path.isdir(sysroot_dir):
                    for target in os.listdir(os.path.join(sysroot_dir, 'usr', 'lib')):
                        arch = _get_android_arch(target.split('-')[0])
                        lib_dir = os.path.join(sysroot_dir, 'usr', 'lib', target)
                        for version in os.listdir(lib_dir):
                            lib_dir_version = os.path.join(lib_dir, version)
                            if os.path.isdir(lib_dir_version):
                                config = NdkConfig(
                                    ndkroot, sysroot_dir, sysroot_dir, [lib_dir_version, lib_dir],
                                    ['-D__ANDROID_API__=%s' % version]
                                )
                                try:
                                    self._versions[int(version)].archs[arch] = config
                                except KeyError:
                                    self._versions[int(version)] = NdkArchConfig({arch: config})

    def get_ndk_for_sdk(self, sdk: str) -> Optional[NdkArchConfig]:
        sdk_number = int(sdk.split('-')[1])
        ndk_versions = sorted([v for v in self._versions.keys() if v <= sdk_number])
        try:
            best_ndk_version = ndk_versions[-1]
        except IndexError:
            return None
        else:
            return self._versions[best_ndk_version]


class AndroidPlatform(_Platform):
    NAME = 'android'

    def __init__(
            self,
            _: build_framework.ConfigurationContext,
            ndk_config: NdkArchConfig,
            sdk_root: str,
            version: str
    ) -> None:
        _Platform.__init__(self)
        self.NAME = self.__class__.NAME + '_' + self.get_android_version(version)
        self.ndk_config = ndk_config
        self.sdk_path = sdk_root
        self.sdk_version = version

    @staticmethod
    def get_android_version(sdk_version: str) -> str:
        versions = {
            '1': '1.0',
            '2': '1.1',
            '3': 'Cupcake_1.5',
            '4': 'Donut_1.6',
            '5': 'Eclair_2.0',
            '6': 'Eclair_2.0.1',
            '7': 'Eclair_2.1',
            '8': 'Froyo_2.2',
            '9': 'Gingerbread_2.3.2',
            '10': 'Gingerbread_2.3.7',
            '11': 'Honeycomb_3.0',
            '12': 'Honeycomb_3.1',
            '13': 'Honeycomb_3.2',
            '14': 'IceCreamSandwich_4.0',
            '15': 'IceCreamSandwich_4.0.3',
            '16': 'JellyBean_4.1',
            '17': 'JellyBean_4.2',
            '18': 'JellyBean_4.3',
            '19': 'KitKat_4.4',
            '20': 'KitKat_4.4W',
            '21': 'Lollipop_5.0',
            '22': 'Lollipop_5.1',
            '23': 'Marshmallow_6.0',
            '24': 'Nougat_7.0',
            '25': 'Nougat_7.1',
            '26': 'Oreo_8.0',
            '27': 'Oreo_8.1',
            '28': 'Pie_9.0',
            '29': '10',
            '30': '11',
        }
        return versions.get(sdk_version, 'api' + sdk_version)

    @staticmethod
    def get_target_folder(arch: str) -> str:
        archs = {'x86': 'x86', 'armv7a': 'armeabi-v7a', 'arm64': 'arm64-v8a', 'amd64': 'x86_64'}
        return archs[arch]

    @staticmethod
    def get_android_c_flags(compiler: _Compiler) -> List[str]:
        arch_flags = {
            'gcc':
                {
                    'x86': [],
                    'amd64': [],
                    'armv7a': ['-march=armv7-a', '-mfloat-abi=softfp', '-mfpu=vfpv3-d16'],
                    'arm64': [],
                },
            'clang':
                {
                    'x86': [],
                    'amd64': [],
                    'armv7a': ['-march=armv7-a', '-mfloat-abi=softfp', '-mfpu=vfpv3-d16'],
                    'arm64': [],
                }
        }  # type: Dict[str, Dict[str, List[str]]]
        return arch_flags[compiler.NAMES[0].lower()].get(compiler.arch, [])

    @staticmethod
    def get_android_ld_flags(compiler: _Compiler) -> List[str]:
        arch_flags = {
            'gcc': {
                'x86': [],
                'amd64': [],
                'armv7a': ['-Wl,--fix-cortex-a8', ],
                'arm64': [],
            },
            'clang': {
                'x86': [],
                'amd64': [],
                'armv7a': ['-Wl,--fix-cortex-a8', ],
                'arm64': [],
            }
        }  # type: Dict[str, Dict[str, List[str]]]
        return arch_flags[compiler.NAMES[0].lower()].get(compiler.arch, [])

    def load_in_env(
            self,
            configuration_context: build_framework.ConfigurationContext,
            compiler: _Compiler
    ) -> None:
        env = configuration_context.env
        arch = compiler.arch
        ndk_config = self.ndk_config.get_ndk_config(arch)
        target_folder = self.get_target_folder(arch)

        env.VALID_PLATFORMS = ['android']
        env.SYSTEM_NAME = 'linux-android'
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, configuration_context.srcnode.name)
        env.cxxprogram_PATTERN = 'lib%s.so'
        env.append_unique('CFLAGS', ['-fPIC'])
        env.append_unique('CXXFLAGS', ['-fPIC'])
        env.append_unique('LINKFLAGS_cprogram', ['-shared', '-Wl,-z,defs', '-llog', '-lc'])
        env.append_unique('LINKFLAGS_cxxprogram', ['-shared', '-Wl,-z,defs', '-llog', '-lc'])
        env.LINK_WITH_PROGRAM = True
        env.STRIP_BINARY = True
        env.CFLAGS_cxxshlib = []
        env.CXXFLAGS_cxxshlib = []
        env.STATIC = True
        env.COMPILER_ABI = 'androideabi'

        env.DEPLOY_ROOTDIR = appname
        env.DEPLOY_BINDIR = os.path.join('lib', target_folder)
        env.DEPLOY_RUNBINDIR = os.path.join('lib', target_folder)
        env.DEPLOY_LIBDIR = os.path.join('lib', target_folder)
        env.DEPLOY_INCLUDEDIR = 'include'
        env.DEPLOY_DATADIR = os.path.join('assets')
        env.DEPLOY_PLUGINDIR = os.path.join('lib', target_folder)
        env.DEPLOY_KERNELDIR = os.path.join('lib', target_folder)

        env.append_value('CFLAGS', self.get_android_c_flags(compiler))
        env.append_value('CXXFLAGS', self.get_android_c_flags(compiler) + ['-nostdinc++'])
        env.append_value('LDFLAGS', self.get_android_ld_flags(compiler))

        env.ANDROID_SDK = self.sdk_version
        env.ANDROID_SDK_PATH = self.sdk_path
        env.ANDROID_NDK_PATH = ndk_config.get_ndkroot()
        env.ANDROID_ARCH = _get_android_arch(arch)
        env.SYSROOT = ndk_config.get_sysroot()
        compiler.sysroot = ndk_config.get_sysroot()

        sysroot_options = ndk_config.get_defines() + [
            '-isystem%s' % os.path.join(compiler.sysroot, 'usr', 'include'),
            '-isystem%s' % os.path.join(compiler.sysroot, 'usr', 'include', compiler.target)
        ]
        env.append_unique('JAVACFLAGS', ['-bootclasspath', os.path.join(self.sdk_path, 'android.jar')])
        env.append_unique('AAPTFLAGS', ['-I', os.path.join(self.sdk_path, 'android.jar')])
        env.append_unique('COMPILER_CXX_INCLUDES', [
            configuration_context.motornode.make_node('extra/android/src/motor/3rdparty/android/libcxx/api').abspath()])

        # if not os.path.isfile(
        #    os.path.
        #    join(ndk_config.get_ndkroot(), 'prebuilt', 'android-%s' % env.ANDROID_ARCH, 'gdbserver', 'gdbserver')
        # ):
        #    raise Errors.WafError('could not find gdbserver for architecture %s' % env.ANDROID_ARCH)

        env.append_value('CFLAGS', sysroot_options)
        env.append_value('CXXFLAGS', sysroot_options)
        env.append_value(
            'LINKFLAGS', ['--sysroot', ndk_config.get_ldsysroot(),
                          '-B%s' % ndk_config.get_libpath()[0]] + ['-L%s' % libpath for libpath in
                                                                   ndk_config.get_libpath()]
        )
        env.append_value('D8FLAGS', ['--lib', os.path.join(self.sdk_path, 'android.jar')])


class AndroidLoader(_Platform):
    NAME = 'android'

    def __init__(self, configuration_context: build_framework.ConfigurationContext) -> None:
        self.conf = configuration_context
        _Platform.__init__(self)

        if waflib.Options.options.android_jdk:
            paths = [
                os.path.join(waflib.Options.options.android_jdk, 'bin'),
                os.path.join(waflib.Options.options.android_jdk, 'jre', 'bin')
            ]
            configuration_context.find_program('javac', path_list=paths)
            configuration_context.find_program('java', path_list=paths)
            configuration_context.find_program('jar', path_list=paths)
            configuration_context.find_program('javadoc', path_list=paths)
        configuration_context.load('javaw')
        configuration_context.env.append_value('JAVACFLAGS', ['-source', '1.7', '-target', '1.7'])
        configuration_context.env.ANDROID_DEBUGKEY = configuration_context.path.parent.make_node(
            'debug.keystore').abspath()
        configuration_context.env.JARSIGNER_FLAGS = [
            '-sigalg', 'MD5withRSA', '-digestalg', 'SHA1', '-keystore', configuration_context.env.ANDROID_DEBUGKEY,
            '-storepass',
            'android', '-keypass', 'android'
        ]
        configuration_context.env.JARSIGNER_KEY = 'androiddebugkey'
        configuration_context.env.APKSIGNER_FLAGS = [
            '--ks', configuration_context.env.ANDROID_DEBUGKEY, '--ks-pass', 'pass:android', '--key-pass',
            'pass:android'
        ]

        sdk_build_tool_path = self.get_build_tool_path(waflib.Options.options.android_sdk_path)
        sdk_tools_paths = self.get_tools_paths(waflib.Options.options.android_sdk_path)
        configuration_context.find_program('adb', path_list=sdk_tools_paths)
        d8 = os.path.join(sdk_build_tool_path, 'lib', 'd8.jar')
        if os.path.isfile(d8):
            configuration_context.env.D8 = d8
        else:
            configuration_context.env.DEX = os.path.join(sdk_build_tool_path, 'lib', 'dx.jar')
            configuration_context.env.DEXCREATE = '--dex'
            configuration_context.env.DEX_TGT_PATTERN = ['--output=%s']
            if not os.path.isfile(configuration_context.env.DEX):
                raise waflib.Errors.WafError('Unable to locate d8.jar/dx.jar')
        configuration_context.find_program('zipalign', var='ZIPALIGN',
                                           path_list=sdk_tools_paths + [sdk_build_tool_path])
        configuration_context.find_program('jarsigner', var='JARSIGNER', mandatory=False)
        configuration_context.find_program('apksigner', var='APKSIGNER', path_list=[sdk_build_tool_path],
                                           mandatory=False)
        if not configuration_context.env.JARSIGNER and not configuration_context.env.APKSIGNER:
            raise waflib.Errors.WafError('Unable to locate jarsigner or apksigner')
        configuration_context.find_program('aapt', path_list=[sdk_build_tool_path])
        configuration_context.find_program('7z', var='_7Z', mandatory=False)

    @staticmethod
    def get_tools_paths(android_path: str) -> List[str]:
        return [os.path.join(android_path, 'platform-tools'), os.path.join(android_path, 'tools')]

    @staticmethod
    def get_build_tool_path(android_path: str) -> str:
        sdk_tools_path = os.path.join(android_path, 'build-tools')
        if os.path.isdir(sdk_tools_path):
            sdk_tools = sorted(os.listdir(sdk_tools_path))
            while sdk_tools:
                sdk_tool = sdk_tools.pop(-1)
                if os.path.isdir(os.path.join(sdk_tools_path, sdk_tool, 'lib')):
                    return os.path.join(sdk_tools_path, sdk_tool)
        raise waflib.Errors.WafError('Android build-tools not installed')

    @staticmethod
    def find_android_sdk(
            ndk_path: str,
            sdk_path: str,
            archs: List[str]
    ) -> List[Tuple[NdkArchConfig, str, List[str], str]]:

        ndk_version_config = NdkVersionConfig(ndk_path)

        platforms_sdk = os.path.join(sdk_path, 'platforms')
        all_sdk_sdks = [p for p in os.listdir(platforms_sdk)]
        sdk_pairs_unfiltered = [(i, ndk_version_config.get_ndk_for_sdk(i)) for i in all_sdk_sdks]
        sdk_pairs = [(i, j) for i, j in sdk_pairs_unfiltered if j is not None]
        sdk_pairs = sorted(sdk_pairs, key=lambda x: _alphanum_key(x[0]))
        if sdk_pairs:
            prefered_sdk = waflib.Options.options.android_sdk
            if prefered_sdk == 'all':
                return [
                    (ndk, os.path.join(platforms_sdk, sdk), ndk.get_valid_archs(archs), sdk.split('-')[1])
                    for sdk, ndk in sdk_pairs
                ]
            elif prefered_sdk:
                if 'android-%s' % prefered_sdk in all_sdk_sdks:
                    sdk = 'android-%s' % prefered_sdk
                    ndk = dict(sdk_pairs)[sdk]
                    return [
                        (ndk, os.path.join(platforms_sdk, sdk), ndk.get_valid_archs(archs), sdk.split('-')[1])
                    ]
                else:
                    sdk, ndk = sdk_pairs[0]
                    waflib.Logs.warn(
                        'could not find android SDK version %s in path %s; using %s' % (
                            prefered_sdk, sdk_path, sdk)
                    )
                    return [
                        (ndk, os.path.join(platforms_sdk, sdk), ndk.get_valid_archs(archs), sdk.split('-')[1])
                    ]
            else:
                sdk, ndk = sdk_pairs[0]
                return [(ndk, os.path.join(platforms_sdk, sdk), ndk.get_valid_archs(archs), sdk.split('-')[1])]
        else:
            raise waflib.Errors.WafError('no SDK for archs')

    def _add_compiler_set(
            self,
            k: Tuple[str, str, str],
            compilers: List[_Compiler]
    ) -> List[Tuple[_Compiler, List[_Compiler], _Platform]]:
        result = []  # type: List[Tuple[_Compiler, List[_Compiler], _Platform]]
        archs = [c.arch for c in compilers]
        try:
            android_sdks = self.find_android_sdk(k[2], waflib.Options.options.android_sdk_path, archs)
        except waflib.Errors.WafError:
            raise
        else:
            for ndk_config, sdk_root, archs, sdk_version in android_sdks:
                valid_compilers = []
                seen = set([])
                for c in compilers:
                    if c.arch in archs and c.arch not in seen:
                        seen.add(c.arch)
                        valid_compilers.append(c)
                if len(valid_compilers) >= 1:
                    result.append(
                        (
                            valid_compilers[0], valid_compilers,
                            AndroidPlatform(self.conf, ndk_config, sdk_root, sdk_version)
                        )
                    )
        return result

    def get_available_compilers(
            self,
            configuration_context: build_framework.ConfigurationContext,
            compiler_list: List[_Compiler]
    ) -> List[Tuple[_Compiler, List[_Compiler], _Platform]]:
        result = []  # type: List[Tuple[_Compiler, List[_Compiler], _Platform]]
        compiler_sets = {}  # type: Dict[str, Dict[Tuple[str, str, str], List[_Compiler]]]
        for compiler in compiler_list:
            for c in [compiler] + compiler.siblings:
                compiler_path = os.path.normpath(c.compiler_c)
                for ndk_path in waflib.Options.options.android_ndk_path.split(','):
                    ndk_path = os.path.normpath(os.path.abspath(ndk_path))
                    if compiler_path.startswith(ndk_path):
                        c_name = c.NAMES[0].lower()
                        try:
                            subset = compiler_sets[c_name]
                        except KeyError:
                            subset = compiler_sets[c_name] = {}
                        k = (c.NAMES[0], c.version, ndk_path)
                        try:
                            subset[k].append(c)
                        except KeyError:
                            subset[k] = [c]
                        break

        # find all GCC targets
        seen = set([])
        all_gcc_compilers = sorted(compiler_sets.get('gcc', {}).items())
        for k, compilers in all_gcc_compilers:
            if (k[0], k[1]) in seen:
                continue
            for c in compilers:
                prebuilt = os.path.join(k[2], 'prebuilt')
                for target in os.listdir(prebuilt):
                    c.directories.append(os.path.join(prebuilt, target, 'bin'))
            try:
                result += self._add_compiler_set(k, compilers)
            except waflib.Errors.WafError as e:
                print(e)
                continue
            else:
                seen.add((k[0], k[1]))

        if all_gcc_compilers:
            for k, compilers in sorted(compiler_sets.get('clang', {}).items()):
                if (k[0], k[1]) in seen:
                    continue
                c = compilers[0]
                clang_compilers = []  # type: List[_Compiler]
                for gcc in all_gcc_compilers[-1][1]:
                    gcc_toolchain = os.path.dirname(os.path.dirname(gcc.compiler_c))
                    extra_args = deepcopy(c.extra_args)
                    extra_args['c'] += ['-target', gcc.target, '-gcc-toolchain', gcc_toolchain]
                    extra_args['cxx'] += ['-target', gcc.target, '-gcc-toolchain', gcc_toolchain]
                    extra_args['link'] += ['-target', gcc.target, '-gcc-toolchain', gcc_toolchain]
                    try:
                        clang_compiler = _Clang(c.compiler_c, c.compiler_cxx, extra_args)
                    except waflib.Errors.WafError:
                        pass
                    else:
                        prebuilt = os.path.join(k[2], 'prebuilt')
                        for target in os.listdir(prebuilt):
                            clang_compiler.directories.append(os.path.join(prebuilt, target, 'bin'))
                        clang_compiler.directories += gcc.directories
                        clang_compiler.target = gcc.target
                        clang_compilers.append(clang_compiler)
                if clang_compilers:
                    try:
                        result += self._add_compiler_set(k, clang_compilers)
                    except waflib.Errors.WafError as e:
                        print(e)
                        continue
                    else:
                        seen.add((k[0], k[1]))
        else:
            for k, compilers in sorted(compiler_sets.get('clang', {}).items()):
                if (k[0], k[1]) in seen:
                    continue
                c = compilers[0]
                clang_compilers = []
                target_dir = os.path.normpath(os.path.join(c.compiler_c, '..', '..', 'lib', 'gcc'))
                try:
                    targets = os.listdir(target_dir)
                except FileNotFoundError:
                    target_dir = os.path.normpath(os.path.join(c.compiler_c, '..', '..', 'sysroot', 'usr', 'lib'))
                    try:
                        targets = os.listdir(target_dir)
                    except FileNotFoundError:
                        targets = []
                for target in targets:
                    extra_args = deepcopy(c.extra_args)
                    extra_args['c'] += ['-target', target]
                    extra_args['cxx'] += ['-target', target]
                    extra_args['link'] += ['-target', target]
                    try:
                        clang_compiler = _Clang(c.compiler_c, c.compiler_cxx, extra_args)
                    except waflib.Errors.WafError:
                        pass
                    else:
                        for path in self.conf.env.EXTRA_PATH:
                            lib_path = os.path.normpath(os.path.join(path, '..', 'lib', 'gcc', target))
                            if os.path.isdir(lib_path):
                                clang_compiler.directories.append(path)
                        prebuilt = os.path.join(k[2], 'prebuilt')
                        for t in os.listdir(prebuilt):
                            clang_compiler.directories.append(os.path.join(prebuilt, t, 'bin'))
                        clang_compiler.target = target
                        clang_compilers.append(clang_compiler)

                if clang_compilers:
                    try:
                        result += self._add_compiler_set(k, clang_compilers)
                    except waflib.Errors.WafError as e:
                        print(e)
                        continue
                    else:
                        seen.add((k[0], k[1]))
        return result


def configure(
        configuration_context: build_framework.ConfigurationContext
) -> None:
    if waflib.Options.options.android_sdk_path or not waflib.Options.options.android_ndk_path:
        configuration_context.start_msg('Checking for Android tools')
        try:
            platform = AndroidLoader(configuration_context)
        except waflib.Errors.WafError as e:
            configuration_context.end_msg(str(e), color='YELLOW')
        else:
            configuration_context.end_msg('done')
            _Platform.platforms.append(platform)
