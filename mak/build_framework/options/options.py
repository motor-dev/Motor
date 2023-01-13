import os
import sys
from motor_typing import TYPE_CHECKING
from waflib import Logs, Configure, Utils

legacy_log_emit_override = Logs.log_handler.emit_override

status_line = None


def log_handler_emit(self, record):
    if status_line is not None:
        global cursor_pos
        self.stream.write('\0338\033[K')
        legacy_log_emit_override(self, record)
        if self.terminator != '\n' and record.msg[-1] != '\n':
            self.stream.write('\033D\033M\0337\n%s' % status_line)
        else:
            self.stream.write('\0337%s' % status_line)
    else:
        legacy_log_emit_override(self, record)


Logs.log_handler.emit_override = log_handler_emit
sys.stdout.write('\0337')


@Configure.conf
def set_status_line(context, line):
    global status_line
    if status_line is not None:
        sys.stdout.write('\r\033[K%s' % line)
    else:
        sys.stdout.write('\0337%s' % line)
    status_line = line


@Configure.conf
def progress_line(context, idx, total, col1, col2):
    """
    Computes a progress bar line displayed when running ``waf -p``

    :returns: progress bar line
    :rtype: string
    """
    if not sys.stdout.isatty():
        return None

    n = len(str(total))

    Utils.rot_idx += 1
    ind = Utils.rot_chr[Utils.rot_idx % 4]

    right = '[%s%s%s]' % (col1, context.timer, col2)
    cols = Logs.get_term_cols() - len(right) + len(col2) + len(col1)
    cmd = context.cmd[:cols]
    fs = "[%%%dd/%%d] %s" % (n, cmd)
    left = fs % (idx, total)

    ratio = ((cols * idx * 8) // total)
    full_length = ratio // 8

    if idx == total:
        bar = '\x1b[30;42m' + cmd + '\x1b[32;100m' + ('\u2588' * (full_length - len(cmd))) + '\x1b[0m'
    elif full_length >= len(cmd):
        subpixel = ' \u258f\u258e\u258d\u258c\u258b\u258a\u2589'
        bar = '\x1b[30;42m' + cmd + '\x1b[32;100m' + ('\u2588' * (full_length - len(cmd))) + subpixel[
            ratio % 8] + (' ' * (cols - full_length - 1)) + '\x1b[0m'
    else:
        subpixel = ' \u258f\u258e\u258d\u258c\u258b\u258a\u2589'
        bar = '\x1b[30;42m' + cmd[:full_length] + '\x1b[32;100m' + subpixel[
            ratio % 8] + '\x1b[37;100m' + cmd[full_length + 1:] + (' ' * (cols - len(cmd))) + '\x1b[0m'
    msg = Logs.indicator % ('', bar, right)

    return msg


def add_package_options(option_context, package_name):
    # type: (Options.OptionsContext, str) -> None
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