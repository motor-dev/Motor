import sys
import build_framework
import waflib.Logs
import waflib.Options
import waflib.Utils
import waflib.Build


def setup(setup_context: build_framework.SetupContext) -> None:
    third_party_node = setup_context.path.make_node('motor/3rdparty')
    setups = []
    setup_context.timer = waflib.Utils.Timer()

    for category in third_party_node.listdir():
        if category[0] != '.':
            category_node = third_party_node.make_node(category)
            for third_party in category_node.listdir():
                setups.append((category, third_party))

    for i, (category, third_party) in enumerate(setups):
        if waflib.Options.options.progress_bar == 1 and sys.stdout.isatty():
            m = build_framework.progress_line(setup_context, i, len(setups) + 1, waflib.Logs.colors.BLUE,
                                              waflib.Logs.colors.NORMAL)
            setup_context.set_status_line(m)
        setup_context.recurse(
            '%s/%s/%s/mak/setup.py' % (third_party_node.abspath(), category, third_party), once=False
        )

    if waflib.Options.options.progress_bar == 1 and sys.stdout.isatty():
        m = build_framework.progress_line(setup_context, len(setups), len(setups) + 1, waflib.Logs.colors.BLUE,
                                          waflib.Logs.colors.NORMAL)
        setup_context.set_status_line(m)

    setup_context.recurse('plugin/compute/opencl/mak/setup.py')
    if waflib.Options.options.progress_bar == 1 and sys.stdout.isatty():
        m = build_framework.progress_line(setup_context, len(setups) + 1, len(setups) + 1, waflib.Logs.colors.BLUE,
                                          waflib.Logs.colors.NORMAL)
        setup_context.set_status_line(m)
