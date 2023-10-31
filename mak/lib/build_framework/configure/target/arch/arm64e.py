from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'arm64e'
    configuration_context.env.VALID_ARCHITECTURES = ['arm64e', 'arm64', 'aarch64']
    configuration_context.env.ARCH_FAMILY = 'arm'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES', ['_ARM', '_ARM64', '_ARM64E', '_AARCH64', '_LP64'])
