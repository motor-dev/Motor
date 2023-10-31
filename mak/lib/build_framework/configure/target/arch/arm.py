from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'arm'
    configuration_context.env.VALID_ARCHITECTURES = ['arm']
    configuration_context.env.ARCH_FAMILY = 'arm'
    configuration_context.env.ARCH_LP64 = False
    configuration_context.env.append_unique('DEFINES', ['_ARM'])
