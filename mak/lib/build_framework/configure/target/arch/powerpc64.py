from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'ppc64'
    configuration_context.env.VALID_ARCHITECTURES = ['ppc64', 'powerpc64']
    configuration_context.env.ARCH_FAMILY = 'ppc'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES', ['_PPC', '_POWERPC', '_PPC64', '_POWERPC64', '_LP64'])
