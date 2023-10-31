from ....options import ConfigurationContext
from . import armv7a


def configure(configuration_context: ConfigurationContext) -> None:
    armv7a.configure(configuration_context)
    configuration_context.env.VALID_ARCHITECTURES = ['armv7k'] + configuration_context.env.VALID_ARCHITECTURES
    configuration_context.env.append_unique('DEFINES', ['_ARM_V7K'])
