from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'ppc64le'
    configuration_context.env.VALID_ARCHITECTURES = ['ppc64le', 'powerpc64le']
    configuration_context.env.ARCH_FAMILY = 'ppc'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES',
                                            ['_PPC', '_POWERPC', '_PPC64', '_POWERPC64', '_PPC64LE', '_POWERPC64LE',
                                             '_LP64'])
