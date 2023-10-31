import build_framework
import waflib.Errors
import waflib.Options

TCLTK_PACKAGE = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/tcltk-%(platform)s.tgz'


def setup(setup_context: build_framework.SetupContext) -> None:
    if 'macos' in setup_context.env.PLATFORMS:
        try:
            node = build_framework.pkg_unpack(
                setup_context,
                'tcltk-%(platform)s',
                TCLTK_PACKAGE,
            )
        except waflib.Errors.WafError:
            pass
        else:
            setup_context.env.TCLTK_BINARY = node.path_from(setup_context.package_node)
            setup_context.env.check_tcltk = True
