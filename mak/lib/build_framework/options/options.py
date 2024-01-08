import os
import waflib.Node
import waflib.Options
from .host import options_host
from .target import options_target
from .commands import options_commands


def add_package_options(option_context: waflib.Options.OptionsContext, package_name: str) -> None:
    gr = option_context.get_option_group('3rd party libraries')
    assert gr is not None

    gr.add_option(
        '--with-%s' % package_name,
        action='store',
        dest='%s_package' % package_name,
        help='source of the ' + package_name +
             ' package. Default is "best" (try pkgconfig, system, prebuilt, source in that order)',
        default='best',
        choices=('best', 'pkgconfig', 'system', 'prebuilt', 'source', 'disabled')
    )


def options_framework(options_context: waflib.Options.OptionsContext) -> None:
    """Creates main option groups and load options for the host and all targets"""
    options_context.add_option_group('SDK paths and options')
    options_context.add_option_group('3rd party libraries')

    gr = options_context.get_option_group('build and install options')
    assert gr is not None

    gr.add_option(
        '--tidy',
        action='store',
        default='auto',
        dest='tidy',
        help=
        'remove unused files from the build and output folders after build; '
        'default is to tidy only if no option is filtering the output folder',
        choices=('force', 'auto', 'none')
    )
    gr.add_option('--nomaster', action='store_true', default=False, dest='nomaster', help='build without master files')
    gr.add_option(
        '--static',
        action='store_true',
        default=False,
        dest='static',
        help=
        'build completely static executable: '
        'All engine components, plugins, samples and kernels will be built into the executable'
    )
    gr.add_option(
        '--dynamic',
        action='store_true',
        default=False,
        dest='dynamic',
        help=
        'build completely dynamic executable: '
        'All engine components, plugins, samples and kernels will be built as shared objects'
    )
    gr.add_option(
        '--werror',
        action='store_true',
        default=False,
        dest='werror',
        help=
        'treat warnings as error'
    )
    gr.add_option('--silent', action='store_true', default=False, dest='silent', help='do not print build log from Waf')

    options_context.add_option(
        '--profile', action='store_true', default=False, dest='profile', help='run WAF in the profiler'
    )

    motornode = getattr(options_context, 'motornode')  # type: waflib.Node.Node
    tool_dir = os.path.join(motornode.abspath(), 'mak', 'lib', 'waftools')
    options_context.load('visualstudio', tooldir=[tool_dir])
    options_context.load('xcode', tooldir=[tool_dir])
    options_context.load('qtcreator', tooldir=[tool_dir])
    options_context.load('vscode', tooldir=[tool_dir])
    options_context.load('cmake', tooldir=[tool_dir])
    options_context.load('clion', tooldir=[tool_dir])

    gr = options_context.add_option_group('configure options')
    gr.add_option(
        '--compilers', action='store', default='', dest='compilers', help='List of compilers to configure for'
    )

    options_host(options_context)
    options_target(options_context)

    for extra in motornode.make_node('extra').listdir():
        if os.path.isfile(os.path.join(motornode.abspath(), 'extra', extra, 'wscript')):
            options_context.recurse(os.path.join(motornode.abspath(), 'extra', extra))

    options_commands(options_context)
