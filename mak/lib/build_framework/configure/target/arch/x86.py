from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'i386'
    configuration_context.env.VALID_ARCHITECTURES = ['x86', 'i386']
    configuration_context.env.ARCH_FAMILY = 'x86'
    configuration_context.env.ARCH_LP64 = False
    configuration_context.env.append_unique('DEFINES', '_X86')
