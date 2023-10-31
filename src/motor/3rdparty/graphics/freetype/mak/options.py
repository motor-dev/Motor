import build_framework
import waflib.Options


def options(options_context: waflib.Options.OptionsContext) -> None:
    build_framework.add_package_options(options_context, 'freetype')
