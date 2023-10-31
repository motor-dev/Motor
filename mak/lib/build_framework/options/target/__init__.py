import os
import shlex
import waflib.Options
from .freebsd import options_target_freebsd
from .linux import options_target_linux
from .macos import options_target_macos
from .solaris import options_target_solaris
from .windows import options_target_windows

from typing import List


def get_jail_sysroots() -> List[str]:
    try:
        with open('/etc/jail.conf', 'r') as jail_conf:
            jail = jail_conf.readlines()
    except (OSError, IOError):
        return []
    else:
        roots = []
        for line in jail:
            line = line.split('#')[0].strip()
            records = line.split('=')
            if len(records) == 2:
                if records[0].strip() == 'path':
                    roots.append(shlex.split(records[1][:-1])[0])
        return roots


def options_target(options_context: waflib.Options.OptionsContext) -> None:
    gr = options_context.add_option_group('configure options')
    gr.add_option('--platforms', action='store', default='', dest='platforms', help="List of platform to configure for")
    sysroots = []
    for path in ('/opt/sys', '/opt/sysroots'):
        try:
            dirs = os.listdir(path)
        except OSError:
            pass
        else:
            for directory in dirs:
                absolute_path = os.path.join(path, directory)
                if os.path.isdir(absolute_path):
                    sysroots.append(absolute_path)

    gr.add_option(
        '--sysroot',
        action='append',
        default=sysroots + get_jail_sysroots(),
        dest='sysroots',
        help="List of directories that map to a platform's sysroot"
    )

    options_target_freebsd(options_context)
    options_target_linux(options_context)
    options_target_macos(options_context)
    options_target_solaris(options_context)
    options_target_windows(options_context)
