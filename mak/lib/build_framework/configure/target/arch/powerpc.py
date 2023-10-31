from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'ppc'
    configuration_context.env.VALID_ARCHITECTURES = ['ppc', 'powerpc']
    configuration_context.env.ARCH_FAMILY = 'ppc'
    configuration_context.env.ARCH_LP64 = False
    configuration_context.env.append_unique('DEFINES', ['_PPC', '_POWERPC'])
