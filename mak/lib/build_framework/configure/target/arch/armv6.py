from ....options import ConfigurationContext
from . import arm


def configure(configuration_context: ConfigurationContext) -> None:
    arm.configure(configuration_context)
    configuration_context.env.VALID_ARCHITECTURES = ['armv6'] + configuration_context.env.VALID_ARCHITECTURES
    configuration_context.env.append_unique('DEFINES', ['_ARM_V6'])
