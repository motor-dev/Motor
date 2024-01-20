import os
import build_framework
import waflib.Errors
import waflib.Options
import waflib.Task
import waflib.TaskGen
import waflib.Tools.c_config

PYTHON_PACKAGE = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/python{version}-%(platform)s.tgz'


def _python_package(
        setup_context: build_framework.SetupContext,
        version: str,
        version_number: str
) -> None:
    try:
        node = build_framework.pkg_unpack(
            setup_context,
            'python{version}-%(platform)s'.format(version=version),
            PYTHON_PACKAGE.format(version=version),
        )
    except waflib.Errors.WafError:
        raise
    else:
        setup_context.env['PYTHON%s_BINARY' % version_number
                          ] = node.path_from(setup_context.package_node)
        setup_context.env['check_python%s' % version_number] = True
        python_library = 'python%s' % version
        python_library_short = 'python%s' % version_number
        for n in node.ant_glob('**/*', remove=False):
            index = n.name.find(python_library)
            if index != -1:
                python_library = os.path.splitext(n.name[index:])[0]
                break
            index = n.name.find(python_library_short)
            if index != -1:
                python_library = os.path.splitext(n.name[index:])[0]
                break
        else:
            raise waflib.Errors.WafError('could not locate Python DLL in package')
        setup_context.env['check_python%s_defines' % version_number] = ['PYTHON_LIBRARY=%s' % python_library]


def _write_test_file(task: waflib.Task.Task) -> None:
    task.outputs[0].write(getattr(task.generator, 'code'))


@waflib.TaskGen.feature("check_python")
@waflib.TaskGen.before_method("process_source")
def check_python_test(task_gen: waflib.TaskGen.task_gen) -> None:
    bld = task_gen.bld
    bld(rule=_write_test_file, target='main.cc', code=getattr(task_gen, 'code'))
    bld(
        features='cxx cxxprogram',
        source='main.cc',
        target='app',
        cxxflags=getattr(task_gen, 'cxxflags'),
        linkflags=getattr(task_gen, 'ldflags'),
        lib=getattr(task_gen, 'libs'),
        use=getattr(task_gen, 'use')
    )


def _python_config(
        setup_context: build_framework.SetupContext,
        version: str,
        var: str = ''
) -> None:
    version_number = version.replace('.', '')
    if not var:
        var = 'python%s' % version_number
    if 'posix' in setup_context.env.VALID_PLATFORMS:
        try:
            cflags, libs, ldflags = build_framework.run_pkg_config(setup_context, 'python-%s-embed' % version)
        except waflib.Errors.WafError:
            try:
                cflags, libs, ldflags = build_framework.run_pkg_config(setup_context, 'python-%s' % version)
            except waflib.Errors.WafError:
                cflags = ['-I/usr/include/python%s' % version]
                ldflags = []
                libs = ['python%s' % version]
        waflib.Tools.c_config.check(
            setup_context,
            compile_filename=[],
            features='check_python',
            msg='check for python %s' % version,
            cxxflags=cflags,
            libs=libs,
            ldflags=ldflags,
            use=[var],
            code="""
                #include <Python.h>
                int main() { Py_InitializeEx(0); return 0; }
            """
        )
        setup_context.env['check_%s' % var] = True
        for lib in libs:
            if lib.startswith('python'):
                setup_context.env['check_%s_defines' % var] = ['PYTHON_LIBRARY=%s' % lib]
                break
        else:
            raise waflib.Errors.WafError('unable to find python library')
    else:
        _python_package(setup_context, version, version_number)


def setup(setup_context: build_framework.SetupContext) -> None:
    if not setup_context.env.PROJECTS:
        setup_context.recurse('tcltk/setup.py')
        build_framework.start_msg_setup(setup_context)
        py_versions = []
        for version in waflib.Options.options.python_versions.split(','):
            try:
                _python_config(setup_context, version)
            except waflib.Errors.WafError:
                pass
            else:
                setup_context.env.append_unique('FEATURES', 'python%s' % version)
                py_versions.append(version)
        if py_versions:
            setup_context.end_msg(', '.join(py_versions))
        else:
            setup_context.end_msg('not found', color='YELLOW')
