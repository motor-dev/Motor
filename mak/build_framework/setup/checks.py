from waflib import Utils, ConfigSet, Errors
from waflib.Configure import conf
from waflib.TaskGen import feature, before_method, after_method, extension
import platform
import os

os_name = platform.uname()[0].lower().split('-')[0]

USE_LIBRARY_CODE = """
%(include)s
extern "C" {
%(include_externc)s
}
#if defined(_WIN32) && !defined(__clang__)
__declspec(dllexport) int motor_test()
{
    return 0;
}
#endif
int main(int argc, char *argv[])
{
    int i;
    %(function)s;
    return i;
}
"""

USE_SDK_CODE = """
#include <iostream>
#include <cstdlib>
#include <cassert>
#include <stdio.h>

int main(int argc, const char *argv[])
{ return EXIT_SUCCESS; }
"""


def extend_path(path, sysroot):
    if path[0] == '=':
        if sysroot:
            return os.path.join(sysroot, path[2:])
        else:
            return path[1:]
    else:
        return path


@feature('cxxtest')
def dummy_cxxtest_feature(task_gen):
    pass


@extension('.mm')
def mm_hook(self, node):
    self.create_compiled_task('cxx', node)


@feature("link_library")
@before_method("process_source")
def link_library_test(self):

    def write_test_file(task):
        task.outputs[0].write(task.generator.code)

    bld = self.bld
    bld(rule=write_test_file, target='main.cc', code=self.code)
    bld(
        features='cxx cxxprogram cxxtest',
        source='main.cc',
        target='app',
        lib=self.libname,
        libpath=self.libpath,
        includes=self.includepath,
        use=self.use
    )


@feature("link_framework")
@before_method("process_source")
def link_framework_test(self):

    def write_test_file(task):
        task.outputs[0].write(task.generator.code)

    bld = self.bld
    bld(rule=write_test_file, target='main.mm', code=self.code)
    env = self.env.derive()
    env.detach()
    env.FRAMEWORK = self.frameworks
    env.FRAMEWORK_ST = ['-framework']
    env.append_unique('CXXFLAGS', ['-F%s' % f for f in self.frameworks])
    if self.sdk:
        env.append_unique('CXXFLAGS', ['-isysroot', self.sdk])
        env.append_unique('LINKFLAGS', ['-isysroot', self.sdk, '-L%s/usr/lib' % self.sdk])
    if self.version:
        env.append_unique('CXXFLAGS', [self.version])
        env.append_unique('LINKFLAGS', [self.version])
    bld(
        features='cxx cxxprogram cxxtest',
        source='main.mm',
        target='app',
        lib=self.libname,
        libpath=self.libpath,
        includes=self.includepath,
        env=env,
        use=self.use
    )


@conf
def check_package(
    self,
    libname,
    path,
    var='',
    libpath=[],
    includepath=[],
    includes=[],
    includes_externc=[],
    functions=[],
    defines=[],
    code=USE_LIBRARY_CODE
):
    if path.find_node('api'):
        includepath = includepath + [path.find_node('api').abspath()]
    if path.find_node('include'):
        includepath = includepath + [path.find_node('include').abspath()]
    for suffix in [''] + ['.%s' % s for s in self.env.VALID_PLATFORMS] + [
        '.%s' % s for s in self.env.VALID_ARCHITECTURES
    ] + ['.%s.%s' % (p, a) for p in self.env.VALID_PLATFORMS for a in self.env.VALID_ARCHITECTURES]:
        if path.find_node('lib' + suffix):
            libpath = libpath + [path.find_node('lib' + suffix).abspath()]
    return self.check_lib(libname, var, libpath, includepath, includes, includes_externc, functions, defines, code)


@conf
def check_lib(
    self,
    libname,
    var='',
    libpath=[],
    includepath=[],
    includes=[],
    includes_externc=[],
    functions=[],
    defines=[],
    code=USE_LIBRARY_CODE
):

    def cut(string):
        if len(string) > 19:
            return string[0:17] + '...'
        else:
            return string

    sysroot = self.env.SYSROOT or ''
    libname = Utils.to_list(libname)
    env = self.env.derive()
    env.detach()
    env.append_unique('DEFINES', defines)
    if not var: var = self.path.parent.name
    try:
        if functions:
            functions = '\n'.join(['i = *(int*)(&%s);' % f for f in functions])
        else:
            functions = 'i = *(int*)0;'
        self.check(
            env=env,
            compile_filename=[],
            features='link_library',
            msg='check for libraries %s' % cut(','.join(libname)),
            libname=libname,
            libpath=[extend_path(p, sysroot) for p in libpath],
            code=code % {
                'include': '\n'.join(['#include <%s>' % i for i in includes]),
                'include_externc': '\n'.join(['#include <%s>' % i for i in includes_externc]),
                'function': functions
            },
            includepath=[extend_path(p, sysroot) for p in includepath],
            use=[],
            envname=self.env.TOOLCHAIN
        )
    except self.errors.ConfigurationError as e:
        pass
    else:
        self.env['check_%s' % var] = True
        self.env.append_unique('check_%s_libs' % var, libname)
        self.env.append_unique('check_%s_libpath' % var, [extend_path(p, sysroot) for p in libpath])
        self.env.append_unique('check_%s_includes' % var, [extend_path(p, sysroot) for p in includepath])
        self.env.append_unique('check_%s_defines' % var, defines)
    return self.env['check_%s' % var]


@conf
def check_header(self, headername, var='', libpath=[], includepath=[], code=USE_LIBRARY_CODE):

    def cut(string):
        if len(string) > 19:
            return string[0:17] + '...'
        else:
            return string

    sysroot = self.env.SYSROOT or ''
    headername = Utils.to_list(headername)
    if not var: var = self.path.parent.name
    try:
        self.check(
            compile_filename=[],
            features='link_library',
            msg='check for header %s' % cut(','.join(headername)),
            libname=[],
            libpath=[extend_path(p, sysroot) for p in libpath],
            code='\n'.join(["#include <%s>" % h for h in headername]) + '\n' + code,
            includepath=[extend_path(p, sysroot) for p in includepath],
            use=[],
            envname=self.env.TOOLCHAIN
        )
    except self.errors.ConfigurationError as e:
        pass
    else:
        self.env['check_%s' % var] = True
        self.env.append_unique('check_%s_includes' % var, [extend_path(p, sysroot) for p in includepath])
        self.env.append_unique('check_%s_libpath' % var, [extend_path(p, sysroot) for p in libpath])
    return self.env['%s_includess' % var]


@conf
def check_framework(
    self,
    frameworks,
    var='',
    libpath=[],
    includepath=[],
    includes=[],
    includes_externc=[],
    functions=[],
    code=USE_LIBRARY_CODE
):

    def cut(string):
        if len(string) > 19:
            return string[0:17] + '...'
        else:
            return string

    frameworks = Utils.to_list(frameworks)
    if not var: var = self.path.parent.name
    try:
        if functions:
            functions = ' + '.join(['*(int*)(&%s)' % f for f in functions])
        else:
            functions = '*(int*)0'
        self.check(
            compile_filename=[],
            features='link_framework',
            msg='check for framework %s' % cut(','.join(frameworks)),
            libname=[],
            frameworks=frameworks,
            libpath=libpath,
            code=code % {
                'include': '\n'.join(['#include <%s>' % i for i in includes]),
                'include_externc': '\n'.join(['#include <%s>' % i for i in includes_externc]),
                'function': functions
            },
            includepath=includepath,
            sdk='',
            version='',
            use=[],
            envname=self.env.TOOLCHAIN
        )
    except self.errors.ConfigurationError as e:
        #Logs.pprint('YELLOW', '-%s' % var, sep=' ')
        pass
    else:
        self.env['check_%s' % var] = True
        self.env.append_unique('check_%s_frameworks' % var, frameworks)
        self.env.append_unique('check_%s_includes' % var, includepath)
        self.env.append_unique('check_%s_libpath' % var, libpath)
        self.env.append_unique('XCODE_FRAMEWORKS', frameworks)
    return self.env['check_%s_frameworks' % var]


@conf
def check_sdk(self, compiler, flags, sdk, version, frameworks=[], libpath=[], includepath=[], code=USE_SDK_CODE):
    env = ConfigSet.ConfigSet()
    env.CXX = compiler
    env.LINK_CXX = compiler
    env.CXXFLAGS = flags
    env.LINKFLAGS = flags
    env.CXX_TGT_F = ['-c', '-o', '']
    env.CXXLNK_TGT_F = ['-o']

    code = '\n'.join(['#include <%s/%s.h>' % (f, f) for f in frameworks]) + '\n' + code
    self.check(
        env=env,
        compile_filename=[],
        features='link_framework',
        msg='check for SDK %s' % os.path.split(sdk)[1],
        libname=[],
        frameworks=frameworks,
        libpath=libpath,
        code=code,
        includepath=includepath,
        sdk=sdk,
        version=version,
        use=[],
        errmsg='not usable',
        compiler=compiler,
        envname=self.env.TOOLCHAIN
    )


@conf
def run_pkg_config(conf, name):
    if conf.env.PKGCONFIG_DISABLE:
        raise Errors.WafError('turned off')
    sysroot = conf.env.SYSROOT or ''

    lib_paths = conf.env.SYSTEM_LIBPATHS[:]
    if conf.env.HOST in conf.env.VALID_PLATFORMS or sysroot:
        lib_paths += ['=/usr/share', '=/usr/local/share', '=/usr/libdata', '=/usr/local/libdata']
    for t in conf.env.TARGETS:
        lib_paths.append('=/usr/lib/%s' % t)
        lib_paths.append('=/usr/libdata/%s' % t)
    lib_paths = [extend_path(l, sysroot) for l in lib_paths]
    lib_paths = [l for l in lib_paths if os.path.isdir(l)]

    seen = set([])

    def _run_pkg_config(name):
        seen.add(name)
        expand = {'pc_sysrootdir': sysroot if sysroot else '/'}
        configs = {}
        for l in lib_paths:
            config_file = os.path.join(l, 'pkgconfig', name + '.pc')
            config_file = os.path.normpath(config_file)
            if os.path.isfile(config_file):
                break
        else:
            raise Errors.WafError('No pkg-config file for library %s' % name)

        with open(config_file, 'r') as config:
            lines = config.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line[0] == '#':
                    continue
                pos = line.find('=')
                pos2 = line.find(':')
                if pos != -1 and (pos2 == -1 or pos2 > pos):
                    var_name = line[:pos].strip()
                    value = line[pos + 1:].strip()
                    if len(value) > 0 and value[0] == '"' and value[-1] == '"':
                        value = value[1:-1]
                    if sysroot and len(value) > 0 and value[0] == '/':
                        value = os.path.join(sysroot, value[1:])
                    value = value.replace('${', '{')
                    value = value.format(value, **expand)
                    expand[var_name] = value
                    continue
                pos = line.find(':')
                if pos != -1:
                    var_name = line[:pos].strip()
                    var_name = var_name.strip()
                    value = line[pos + 1:].strip()
                    value = value.replace('${', '{')
                    value = value.format(value, **expand)
                    value = value.strip()
                    if var_name in ('Requires', 'Requires.private'):
                        configs[var_name] = sum([x.strip().split() for x in value.split(',')], [])
                    else:
                        configs[var_name] = [x.strip() for x in value.split()]
        cflags = []
        libs = []
        ldflags = []
        skip = False
        for d in configs.get('Requires', []): # + configs.get('Requires.private', []):
            if skip:
                skip = False
            elif d in ('=', '<', '<=', '>', '>='):
                skip = True
            else:
                if d not in seen:
                    dep_flags = _run_pkg_config(d)
                    cflags += dep_flags[0]
                    libs += dep_flags[1]
                    ldflags += dep_flags[2]
        for f in configs.get('Cflags') or []:
            if f.startswith('-I'):
                include = f[2:]
                if include[0] == '/' and not include.startswith(sysroot):
                    include = os.path.join(sysroot, include[1:])
                if include not in cflags:
                    cflags += [conf.env.IDIRAFTER, include]
            else:
                if f not in cflags:
                    cflags.append(f)
        for f in configs.get('Libs') or []:
            if f.startswith('-l'):
                libs.append(f[2:])
            elif f[0:2] == '-L':
                libdir = f[2:]
                if libdir[0] == '/' and not libdir.startswith(sysroot):
                    libdir = os.path.join(sysroot, libdir)
                if '-L%s' % libdir not in ldflags:
                    ldflags += ['-L%s' % libdir]
            else:
                ldflags.append(f)
        return cflags, libs, ldflags

    return _run_pkg_config(name)


@conf
def pkg_config(conf, name, var=''):
    if 'windows' in conf.env.VALID_PLATFORMS:
        raise Errors.WafError('pkg_config disabled on Windows')
    if not var: var = conf.path.parent.name
    cflags, libs, ldflags = conf.run_pkg_config(name)
    conf.env['check_%s' % var] = True
    conf.env['check_%s_cflags' % var] += cflags
    conf.env['check_%s_cxxflags' % var] += cflags
    conf.env['check_%s_ldflags' % var] += ldflags
    conf.env['check_%s_libs' % var] += libs


def multiarch_setup(conf):
    conf.load('c_config')
