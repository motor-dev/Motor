from ....options import ConfigurationContext
from . import armv7


def configure(configuration_context: ConfigurationContext) -> None:
    armv7.configure(configuration_context)
    configuration_context.env.VALID_ARCHITECTURES = ['armv7a'] + configuration_context.env.VALID_ARCHITECTURES
    configuration_context.env.append_unique('DEFINES', ['_ARM_V7A'])
