from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'aarch32'
    configuration_context.env.VALID_ARCHITECTURES = ['aarch32', 'aarch64']
    configuration_context.env.ARCH_FAMILY = 'arm'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES', ['_ARM', '_ARM64', '_AARCH64', '_AARCH32', '_LP64'])
