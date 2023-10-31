from ..options import ConfigurationContext


def configure_package(configuration_context: ConfigurationContext) -> None:
    configuration_context.setenv('packages')
    configuration_context.env['PACKAGE_REPOS'] = {}
    configuration_context.variant = ''
