import os
from motor_typing import TYPE_CHECKING


def add_package_options(option_context, package_name):
    # type: (Options.OptionsContext) -> None
    gr = option_context.get_option_group('3rd party libraries')
    gr.add_option(
        '--with-%s' % package_name,
        action='store',
        dest='%s_package' % package_name,
        help='source of the ' + package_name +
        ' package. Default is "best" (try pkgconfig, system, prebuilt, source in that order)',
        default='best',
        choices=('best', 'pkgconfig', 'system', 'prebuilt', 'source', 'disabled')
    )


def options(option_context):
    # type: (Options.OptionsContext) -> None
    "Creates main option groups and load options for the host and all targets"
    option_context.add_option_group('SDK paths and options')
    option_context.add_option_group('3rd party libraries')
    option_context.add_package_options = lambda package_name: add_package_options(option_context, package_name)

    gr = option_context.get_option_group('build and install options')
    gr.add_option(
        '--tidy',
        action='store',
        default='auto',
        dest='tidy',
        help=
        'remove unused files from the build and output folders after build; default is to tidy only if no option is filtering the output folder',
        choices=('force', 'auto', 'none')
    )
    gr.add_option('--nomaster', action='store_true', default=False, dest='nomaster', help='build without master files')
    gr.add_option(
        '--static',
        action='store_true',
        default=False,
        dest='static',
        help=
        'build completely static executable: All engine components, plugins, samples and kernels will be built into the executable'
    )
    gr.add_option(
        '--dynamic',
        action='store_true',
        default=False,
        dest='dynamic',
        help=
        'build completely dynamic executable: All engine components, plugins, samples and kernels will be built as shared objects'
    )
    gr.add_option('--silent', action='store_true', default=False, dest='silent', help='do not print build log from Waf')

    option_context.add_option(
        '--profile', action='store_true', default=False, dest='profile', help='run WAF in the profiler'
    )

    tool_dir = os.path.join(option_context.motornode.abspath(), 'mak', 'tools')
    option_context.load('visualstudio', tooldir=[tool_dir])
    option_context.load('xcode', tooldir=[tool_dir])
    option_context.load('netbeans', tooldir=[tool_dir])
    option_context.load('eclipse', tooldir=[tool_dir])
    option_context.load('qtcreator', tooldir=[tool_dir])
    option_context.load('vscode', tooldir=[tool_dir])
    option_context.load('sublime', tooldir=[tool_dir])
    option_context.load('clangd', tooldir=[tool_dir])

    option_context.recurse('compilers.py')
    option_context.recurse('host/host.py')
    option_context.recurse('target/target.py')
    #device.options(opt)
    for extra in option_context.motornode.make_node('extra').listdir():
        if os.path.isfile(os.path.join(option_context.motornode.abspath(), 'extra', extra, 'wscript')):
            option_context.recurse(os.path.join(option_context.motornode.abspath(), 'extra', extra))

    option_context.recurse('commands.py')


if TYPE_CHECKING:
    from waflib import Options