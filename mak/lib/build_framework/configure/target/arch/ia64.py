from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'ia64'
    configuration_context.env.VALID_ARCHITECTURES = ['ia64', 'itanium']
    configuration_context.env.ARCH_FAMILY = 'ia64'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES', ['_IA64', '_LP64'])
