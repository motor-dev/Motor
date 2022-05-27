from waflib import Logs, Options, Build, Utils
import sys


def setup(configuration_context):
    third_party_node = configuration_context.path.make_node('motor/3rdparty')
    setups = []
    configuration_context.__class__.progress_line = Build.BuildContext.progress_line
    configuration_context.timer = Utils.Timer()

    for category in third_party_node.listdir():
        if category[0] != '.':
            category_node = third_party_node.make_node(category)
            for third_party in category_node.listdir():
                setups.append((category, third_party))
    for i, (category, third_party) in enumerate(setups):
        if Options.options.progress_bar == 1 and sys.stdout.isatty():
            m = configuration_context.progress_line(i, len(setups) + 1, Logs.colors.BLUE, Logs.colors.NORMAL)
            Logs.info(
                m,
                extra={
                    'stream': sys.stdout,
                    'terminator': '',
                    'c1': Logs.colors.cursor_off,
                    'c2': Logs.colors.cursor_on
                }
            )
        configuration_context.recurse(
            '%s/%s/%s/mak/setup.py' % (third_party_node.abspath(), category, third_party), once=False
        )

    if Options.options.progress_bar == 1 and sys.stdout.isatty():
        m = configuration_context.progress_line(len(setups), len(setups) + 1, Logs.colors.BLUE, Logs.colors.NORMAL)
        Logs.info(
            m,
            extra={
                'stream': sys.stdout,
                'terminator': '',
                'c1': Logs.colors.cursor_off,
                'c2': Logs.colors.cursor_on
            }
        )
    configuration_context.recurse('plugin/compute/opencl/mak/setup.py')
    if Options.options.progress_bar == 1 and sys.stdout.isatty():
        m = configuration_context.progress_line(len(setups) + 1, len(setups) + 1, Logs.colors.BLUE, Logs.colors.NORMAL)
        Logs.info(m, extra={'stream': sys.stdout, 'c1': Logs.colors.cursor_off, 'c2': Logs.colors.cursor_on})
