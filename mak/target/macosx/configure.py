# set MacOS X specific options

from waflib import Configure, Options, Context, Errors, Utils
from waflib.Configure import conf
import os
import re


class Darwin(Configure.ConfigurationContext.Platform):
    NAME = 'Darwin'
    SDK_NAME = 'Darwin'
    OS_NAME = 'darwin'
    SUPPORTED_TARGETS = (re.compile('.*-darwin.*'),)

    def __init__(self, conf, sdk = None):
        Configure.ConfigurationContext.Platform.__init__(self)
        self.sdk = sdk
        self.conf = conf
        if sdk:
            self.NAME = self.__class__.NAME + sdk[0]
            self.directories += sdk[2]


    def get_available_compilers(self, compiler_list):
        result = []
        compiler_sets = {}
        for c in compiler_list:
            for r in self.SUPPORTED_TARGETS:
                if r.match(c.target):
                    k = (c.NAMES[0], c.version)
                    try:
                        compiler_sets[k].append(c)
                    except KeyError:
                        compiler_sets[k] = [c]
                    break
        for k in sorted(compiler_sets.keys()):
            compilers = compiler_sets[k]
            try:
                compilers, sdk = self.get_best_compilers_sdk(compilers)
            except Errors.WafError as e:
                continue
            else:
                if len(compilers) > 1:
                    result.append((compilers[0], compilers, self.__class__(self.conf, sdk)))
                else:
                    result.append((compilers[0], [], self.__class__(self.conf, sdk)))
        return result

    def load_in_env(self, conf, compiler):
        self.CFLAGS_cshlib = ['-fPIC']
        platform = self.SDK_NAME.lower()
        p1 = os.path.join(self.sdk[1], 'usr', 'bin')
        p2 = os.path.dirname(compiler.compiler_c)
        conf.find_program('lipo')
        if not conf.find_program('dsymutil', path_list=[p1, p2], mandatory=False):
            conf.find_program('dsymutil')
        if not conf.find_program('strip', path_list = [p1, p2], mandatory=False):
            conf.find_program('strip')
        conf.env.ABI = 'mach_o'
        conf.env.VALID_PLATFORMS = self.PLATFORMS + ['darwin']
        conf.env.XCODE_SDKROOT = platform
        conf.env.XCODE_ABI = 'mach_o'
        conf.env.XCODE_SUPPORTEDPLATFORMS = platform
        conf.env.pymodule_PATTERN = '%s.so'

        appname = getattr(Context.g_module, Context.APPNAME, conf.srcnode.name)
        conf.env.DEPLOY_ROOTDIR = os.path.join(appname + '.app', 'Contents')
        conf.env.DEPLOY_BINDIR = os.path.join(appname + '.app', 'Contents', 'MacOS')
        conf.env.DEPLOY_RUNBINDIR = os.path.join(appname + '.app', 'Contents', 'MacOS')
        conf.env.DEPLOY_LIBDIR = 'lib'
        conf.env.DEPLOY_INCLUDEDIR = 'include'
        share = os.path.join(appname + '.app', 'Contents', 'share', 'bugengine')
        conf.env.DEPLOY_DATADIR = share
        conf.env.DEPLOY_PLUGINDIR = os.path.join(share, 'plugin')
        conf.env.DEPLOY_KERNELDIR = os.path.join(share, 'kernel')
        conf.env.append_unique('DEFINES', ['_BSD_SOURCE'])

        conf.env.MACOSX_SDK = os.path.splitext(os.path.basename(self.sdk[1]))[0]
        conf.env.XCODE_SDK_PATH = self.sdk[1]
        conf.env.SYSROOT = self.sdk[1]
        conf.env.append_unique('CFLAGS', ['-m%s-version-min=%s'%(self.OS_NAME, self.sdk[0]), '-isysroot', self.sdk[1]])
        conf.env.append_unique('CXXFLAGS', ['-m%s-version-min=%s'%(self.OS_NAME, self.sdk[0]),
                                            '-isysroot', self.sdk[1]])
        conf.env.append_unique('LINKFLAGS', ['-m%s-version-min=%s'%(self.OS_NAME, self.sdk[0]),
                                             '-isysroot', self.sdk[1], '-L%s/usr/lib'%self.sdk[1]])
        conf.env.CFLAGS_cshlib = ['-fPIC']
        conf.env.CXXFLAGS_cxxshlib = ['-fPIC']

    platform_sdk_re = re.compile('.*/Platforms/\w*\.platform/Developer/SDKs/[\.\w]*\.sdk')
    old_sdk_re = re.compile('.*/SDKs/[\.\w]*\.sdk')
    def match(self, compiler, sdk_path, all_sdks):
        def get_paths(sdk_path):
            if self.platform_sdk_re.match(sdk_path):
                platform_path = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(sdk_path))))
                developer_path, d = os.path.split(platform_path)
                while d and not d.startswith('Developer'):
                    developer_path, d = os.path.split(developer_path)
            elif self.old_sdk_re.match(sdk_path):
                platform_path = os.path.normpath(os.path.dirname(os.path.dirname(sdk_path)))
                developer_path, d = os.path.split(platform_path)
            else:
                platform_path = os.path.normpath(os.path.dirname(os.path.dirname(sdk_path)))
                developer_path, d = os.path.split(platform_path)
            developer_path = os.path.join(developer_path, d)
            if platform_path[-1] != '/':
                platform_path += '/'
            if developer_path[-1] != '/':
                developer_path += '/'
            return platform_path, developer_path
        compiler_path = os.path.normpath(compiler.compiler_c)
        platform_path, developer_path = get_paths(sdk_path)
        if compiler_path.startswith(platform_path):
            return True
        for sdk_version, sdk_archs, sdk_path in all_sdks:
            ppath, dpath = get_paths(sdk_path)
            if compiler_path.startswith(ppath):
                return False
        if compiler_path.startswith(developer_path):
            return True
        for sdk_version, sdk_archs, sdk_path in all_sdks:
            ppath, dpath = get_paths(sdk_path)
            if compiler_path.startswith(dpath):
                return False
        return True


    def get_best_compilers_sdk(self, compilers):
        all_archs = []
        for compiler in sorted(compilers, key = lambda x: x.name()):
            if compiler.arch not in all_archs:
                all_archs.append(compiler.arch)

        try:
            sdk_number_min = getattr(Options.options, '%s_sdk_min' % self.OS_NAME)
        except AttributeError:
            sdk_number_min = ''
        sdk_number_min = sdk_number_min and sdk_number_min.split('.') or []
        try:
            sdk_number_max = getattr(Options.options, '%s_sdk_max' % self.OS_NAME)
        except AttributeError:
            sdk_number_max = ''
        sdk_number_max = sdk_number_max and sdk_number_max.split('.') or []
        sdks = []
        relpath = os.path.join('Platforms', '%s.platform'%self.SDK_NAME, 'Developer', 'SDKs')

        try:
            all_sdks = self.conf.darwin_sdks[self.SDK_NAME]
        except KeyError:
            raise Errors.WafError('No SDK detected for platform %s' % self.SDK_NAME)
        else:
            best_sdk = (None, None, [], [])
            for sdk_version, sdk_archs, sdk_path in all_sdks:
                if len(best_sdk[2]) >= len(sdk_archs):
                    break
                sdk_option = '-m%s-version-min=%s'%(self.OS_NAME, '.'.join(sdk_version))
                if sdk_number_max and sdk_version > sdk_number_max:
                    continue
                if sdk_number_min and sdk_version < sdk_number_min:
                    continue
                sdk_compilers = []
                sdk_bin_paths = [i for i in [
                        os.path.normpath(os.path.join(sdk_path, 'usr', 'bin')),
                        os.path.normpath(os.path.join(sdk_path, '..', '..', 'usr', 'bin')),
                        os.path.normpath(os.path.join(sdk_path, '..', '..', '..', '..', '..', 'usr', 'bin')),
                    ] if os.path.isdir(i) and i != '/usr/bin']
                for a in sdk_archs:
                    for c in compilers:
                        if self.match(c, sdk_path, all_sdks) and c.arch == a:
                            r, out, err = c.run_cxx([sdk_option, '-Wl,-rpath,.', '-x', 'c++', '-isysroot', sdk_path, '-'],
                                                    '#include <stdio.h>\n#include <iostream>\nint main() { printf(0); return 0; }\n')
                            if r == 0:
                                sdk_compilers.append(c)
                                break
                            else:
                                #print(err)
                                pass
                    else:
                        #print('no compiler for arch %s'%a)
                        pass
                if len(sdk_compilers) > len(best_sdk[2]):
                    best_sdk = ('.'.join(sdk_version), sdk_path, sdk_compilers, sdk_bin_paths)
            if best_sdk[2]:
                return best_sdk[2], (best_sdk[0], best_sdk[1], best_sdk[3])
            else:
                raise Errors.WafError('No SDK for compiler %s' % compilers[0].compiler_c)

Configure.ConfigurationContext.Darwin = Darwin

class MacOSX(Darwin):
    NAME = 'MacOSX'
    PLATFORMS = ['macosx', 'pc']
    SDK_NAME = 'MacOSX'
    OS_NAME = 'macosx'

    def __init__(self, conf, sdk = None):
        Darwin.__init__(self, conf, sdk)



def options(opt):
    gr = opt.get_option_group('SDK paths and options')
    gr.add_option( '--macosx-sdk-min',
                    action='store',
                    default='',
                    dest='macosx_sdk_min',
                    help='Minimum version of the MacOS X SDK to target')
    gr.add_option( '--macosx-sdk-max',
                    action='store',
                    default='',
                    dest='macosx_sdk_max',
                    help='Maximum version of the MacOS X SDK to target')



def configure(conf):
    conf.platforms.append(MacOSX(conf))
