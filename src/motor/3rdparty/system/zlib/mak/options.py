import waflib.Options
import build_framework


def options(options_context: waflib.Options.OptionsContext) -> None:
    build_framework.add_package_options(options_context, 'zlib')
    build_framework.add_package_options(options_context, 'minizip')
