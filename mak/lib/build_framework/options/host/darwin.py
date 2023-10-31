import os
import sys
import waflib.Options
import waflib.Utils
import waflib.TaskGen
import waflib.Tools.c_osx
from typing import Union


@waflib.TaskGen.feature('c', 'cxx')
def set_macosx_deployment_target(_: waflib.TaskGen.task_gen) -> None:
    pass


def options_host_darwin(options_context: waflib.Options.OptionsContext) -> None:
    sdks = ['/%s' % d for d in os.listdir('/') if d.startswith('Developer')]
    sdks += [
        os.path.join('/', 'Applications', d, 'Contents', 'Developer') for d in os.listdir('/Applications')
        if d.startswith('Xcode')
    ]
    if os.path.isdir('/Library/Developer/CommandLineTools'):
        sdks += ['/Library/Developer/CommandLineTools']
    try:
        p = waflib.Utils.subprocess.Popen(
            ['xcode-select', '--print-path'],
            stdin=waflib.Utils.subprocess.PIPE,
            stdout=waflib.Utils.subprocess.PIPE,
            stderr=waflib.Utils.subprocess.PIPE
        )
        out = p.communicate()[0]  # type: Union[str, bytes]
    except OSError:
        pass
    else:
        if not isinstance(out, str):
            out = out.decode(sys.stdout.encoding)
        out = out.split('\n')[0]
        if out not in sdks:
            sdks.append(out)
    options_context.add_option(
        '--xcode-sdks',
        action='store',
        default=','.join(sdks),
        dest='xcode_sdks',
        help='Paths of the different XCode SDKs'
    )
