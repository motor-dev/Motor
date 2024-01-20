import platform
import os
import waflib.Utils
import waflib.ConfigSet
import waflib.Errors
import waflib.TaskGen
import waflib.Node
import waflib.Task
import waflib.Tools.c_config
from typing import Dict, List, Optional, Tuple
from ..options import SetupContext
from ..build import create_compiled_task

os_name = platform.uname()[0].lower().split('-')[0]

USE_LIBRARY_CODE = """
%(include)s
extern "C" {
%(include_externc)s
}
#if defined(_MSC_VER)
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


def _extend_path(path: str, sysroot: str) -> str:
    if path[0] == '=':
        if sysroot:
            return os.path.join(sysroot, path[2:])
        else:
            return path[1:]
    else:
        return path


def _cut(string: str) -> str:
    if len(string) > 19:
        return string[0:17] + '...'
    else:
        return string


def _write_test_file(task: waflib.Task.Task) -> None:
    task.outputs[0].write(getattr(task.generator, 'code'))


@waflib.TaskGen.feature('cxxtest')
def dummy_cxxtest_feature(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.extension('.mm')
def mm_hook(self: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    create_compiled_task(self, 'cxx', node)


@waflib.TaskGen.feature('link_library')
@waflib.TaskGen.before_method('process_source')
def link_library_test(self: waflib.TaskGen.task_gen) -> None:
    bld = self.bld
    code = getattr(self, 'code')  # type: str
    libname = getattr(self, 'libname')  # type: List[str]
    libpath = getattr(self, 'libpath')  # type: List[str]
    includepath = getattr(self, 'includepath')  # type: List[str]
    use = getattr(self, 'use')  # type: List[str]
    bld(rule=_write_test_file, target='main.cc', code=code)
    bld(
        features='cxx cxxprogram cxxtest',
        source='main.cc',
        target='app',
        lib=libname,
        libpath=libpath,
        includes=includepath,
        use=use
    )


@waflib.TaskGen.feature('link_framework')
@waflib.TaskGen.before_method('process_source')
def link_framework_test(self: waflib.TaskGen.task_gen) -> None:
    bld = self.bld
    code = getattr(self, 'code')  # type: str
    libname = getattr(self, 'libname')  # type: List[str]
    libpath = getattr(self, 'libpath')  # type: List[str]
    includepath = getattr(self, 'includepath')  # type: List[str]
    frameworks = getattr(self, 'frameworks')  # type: List[str]
    sdk = getattr(self, 'sdk')  # type: str
    version = getattr(self, 'version')  # type: str
    use = getattr(self, 'use')  # type: List[str]

    bld(rule=_write_test_file, target='main.mm', code=code)
    env = self.env.derive()
    env.detach()
    env.FRAMEWORKPATH_ST = '-F%s'
    env.FRAMEWORK = frameworks
    env.FRAMEWORK_ST = ['-framework']
    if sdk:
        env.append_unique('CXXFLAGS', ['-isysroot', sdk])
        env.append_unique('LINKFLAGS', ['-isysroot', sdk, '-L%s/usr/lib' % sdk])
    if version:
        env.append_unique('CXXFLAGS', [version])
        env.append_unique('LINKFLAGS', [version])
    bld(
        features='cxx cxxprogram cxxtest',
        source='main.mm',
        target='app',
        lib=libname,
        libpath=libpath,
        includes=includepath,
        env=env,
        use=use
    )


def check_package(
        setup_context: SetupContext,
        libname: List[str],
        path: waflib.Node.Node,
        var: str = '',
        libpath: Optional[List[str]] = None,
        includepath: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        includes_externc: Optional[List[str]] = None,
        functions: Optional[List[str]] = None,
        defines: Optional[List[str]] = None,
        code: str = USE_LIBRARY_CODE
) -> bool:
    includepath = includepath or []
    libpath = libpath or []
    node = path.find_node('api')
    if node is not None:
        includepath = includepath + [node.abspath()]
    node = path.find_node('include')
    if node is not None:
        includepath = includepath + [node.abspath()]

    for suffix in [''] + ['.%s' % s for s in setup_context.env.VALID_PLATFORMS] + [
        '.%s' % s for s in setup_context.env.VALID_ARCHITECTURES
    ] + ['.%s.%s' % (p, a) for p in setup_context.env.VALID_PLATFORMS for a in
         setup_context.env.VALID_ARCHITECTURES]:
        node = path.find_node('lib' + suffix)
        if node is not None:
            libpath = libpath + [node.abspath()]
    return check_lib(setup_context, libname, var, libpath, includepath, includes, includes_externc, functions,
                     defines, code)


def check_lib(
        setup_context: SetupContext,
        libname: List[str],
        var: str = '',
        libpath: Optional[List[str]] = None,
        includepath: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        includes_externc: Optional[List[str]] = None,
        functions: Optional[List[str]] = None,
        defines: Optional[List[str]] = None,
        code: str = USE_LIBRARY_CODE
) -> bool:
    sysroot = setup_context.env.SYSROOT or ''
    libname = waflib.Utils.to_list(libname)
    env = setup_context.env.derive()
    env.detach()
    if defines is not None:
        env.append_unique('DEFINES', defines)
    if not var:
        var = setup_context.path.parent.name
    try:
        if functions:
            function_code = '\n'.join(['i = *(int*)(&%s);' % f for f in functions])
        else:
            function_code = 'i = *(int*)0;'
        waflib.Tools.c_config.check(
            setup_context,
            env=env,
            compile_filename=[],
            features='link_library',
            msg='check for libraries %s' % _cut(','.join(libname)),
            libname=libname,
            libpath=[_extend_path(p, sysroot) for p in (libpath or [])],
            code=code % {
                'include': '\n'.join(['#include <%s>' % i for i in (includes or [])]),
                'include_externc': '\n'.join(['#include <%s>' % i for i in (includes_externc or [])]),
                'function': function_code
            },
            includepath=[_extend_path(p, sysroot) for p in (includepath or [])],
            use=[],
            envname=setup_context.env.TOOLCHAIN
        )
    except waflib.Errors.ConfigurationError:
        pass
    else:
        setup_context.env['check_%s' % var] = True
        setup_context.env.append_unique('check_%s_libs' % var, libname)
        setup_context.env.append_unique('check_%s_libpath' % var,
                                        [_extend_path(p, sysroot) for p in (libpath or [])])
        setup_context.env.append_unique('check_%s_includes' % var,
                                        [_extend_path(p, sysroot) for p in (includepath or [])])
        setup_context.env.append_unique('check_%s_defines' % var, defines or [])
    return setup_context.env['check_%s' % var]


def check_header(
        setup_context: SetupContext,
        headername: List[str],
        var: str = '',
        libpath: Optional[List[str]] = None,
        includepath: Optional[List[str]] = None,
        code: str = USE_LIBRARY_CODE
) -> List[str]:
    sysroot = setup_context.env.SYSROOT or ''
    headername = waflib.Utils.to_list(headername)
    if not var:
        var = setup_context.path.parent.name
    try:
        waflib.Tools.c_config.check(
            setup_context,
            compile_filename=[],
            features='link_library',
            msg='check for header %s' % _cut(','.join(headername)),
            libname=[],
            libpath=[_extend_path(p, sysroot) for p in (libpath or [])],
            code='\n'.join(["#include <%s>" % h for h in headername]) + '\n' + code,
            includepath=[_extend_path(p, sysroot) for p in (includepath or [])],
            use=[],
            envname=setup_context.env.TOOLCHAIN
        )
    except waflib.Errors.ConfigurationError:
        pass
    else:
        setup_context.env['check_%s' % var] = True
        setup_context.env.append_unique('check_%s_includes' % var,
                                        [_extend_path(p, sysroot) for p in (includepath or [])])
        setup_context.env.append_unique('check_%s_libpath' % var,
                                        [_extend_path(p, sysroot) for p in (libpath or [])])
    return setup_context.env['%s_includes' % var]


def check_framework(
        setup_context: SetupContext,
        frameworks: List[str],
        var: str = '',
        libpath: Optional[List[str]] = None,
        includepath: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        includes_externc: Optional[List[str]] = None,
        functions: Optional[List[str]] = None,
        code: str = USE_LIBRARY_CODE
) -> List[str]:
    frameworks = waflib.Utils.to_list(frameworks)
    if not var:
        var = setup_context.path.parent.name
    try:
        if functions:
            function_code = ' + '.join(['*(int*)(&%s)' % f for f in functions])
        else:
            function_code = '*(int*)0'
        waflib.Tools.c_config.check(
            setup_context,
            compile_filename=[],
            features='link_framework',
            msg='check for framework %s' % _cut(','.join(frameworks)),
            libname=[],
            frameworks=frameworks,
            libpath=libpath or [],
            code=code % {
                'include': '\n'.join(['#include <%s>' % i for i in (includes or [])]),
                'include_externc': '\n'.join(['#include <%s>' % i for i in (includes_externc or [])]),
                'function': function_code
            },
            includepath=includepath or [],
            sdk='',
            version='',
            use=[],
            envname=setup_context.env.TOOLCHAIN
        )
    except waflib.Errors.ConfigurationError:
        pass
    else:
        setup_context.env['check_%s' % var] = True
        setup_context.env.append_unique('check_%s_frameworks' % var, frameworks)
        setup_context.env.append_unique('check_%s_includes' % var, includepath or [])
        setup_context.env.append_unique('check_%s_libpath' % var, libpath or [])
        setup_context.env.append_unique('XCODE_FRAMEWORKS', frameworks)
    return setup_context.env['check_%s_frameworks' % var]


def run_pkg_config(
        setup_context: SetupContext, name: str
) -> Tuple[List[str], List[str], List[str]]:
    if setup_context.env.PKGCONFIG_DISABLE:
        raise waflib.Errors.WafError('turned off')
    sysroot = setup_context.env.SYSROOT or ''

    lib_paths = setup_context.env.SYSTEM_LIBPATHS[:]
    if setup_context.env.HOST in setup_context.env.VALID_PLATFORMS or sysroot:
        lib_paths += ['=/usr/share', '=/usr/local/share', '=/usr/libdata', '=/usr/local/libdata']
    for t in setup_context.env.TARGETS:
        lib_paths.append('=/usr/lib/%s' % t)
        lib_paths.append('=/usr/libdata/%s' % t)
    lib_paths = [_extend_path(p, sysroot) for p in lib_paths]
    lib_paths = [p for p in lib_paths if os.path.isdir(p)]

    seen = set([])

    def _run_pkg_config(pkg_name: str) -> Tuple[List[str], List[str], List[str]]:
        seen.add(pkg_name)
        expand = {'pc_sysrootdir': sysroot if sysroot else '/'}
        configs = {}  # type: Dict[str,List[str]]
        for p in lib_paths:
            config_file = os.path.join(p, 'pkgconfig', pkg_name + '.pc')
            config_file = os.path.normpath(config_file)
            if os.path.isfile(config_file):
                break
        else:
            raise waflib.Errors.WafError('No pkg-config file for library %s' % pkg_name)

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
        for d in configs.get('Requires', []):  # + configs.get('Requires.private', []):
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
                    cflags += [setup_context.env.IDIRAFTER, include]
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


def pkg_config(setup_context: SetupContext,
               name: str,
               var: str = '') -> None:
    if 'windows' in setup_context.env.VALID_PLATFORMS:
        raise waflib.Errors.WafError('pkg_config disabled on Windows')
    if not var:
        var = setup_context.path.parent.name
    cflags, libs, ldflags = run_pkg_config(setup_context, name)
    setup_context.env['check_%s' % var] = True
    setup_context.env['check_%s_cflags' % var] += cflags
    setup_context.env['check_%s_cxxflags' % var] += cflags
    setup_context.env['check_%s_ldflags' % var] += ldflags
    setup_context.env['check_%s_libs' % var] += libs


def multiarch_setup_checks(setup_context: SetupContext) -> None:
    setup_context.load(['c_config'])
