from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'arm64_32'
    configuration_context.env.VALID_ARCHITECTURES = ['arm64_32', 'aarch64_32']
    configuration_context.env.ARCH_FAMILY = 'arm'
    configuration_context.env.ARCH_LP64 = False
    configuration_context.env.append_unique('DEFINES', ['_ARM', '_ARM64', '_AARCH64', '_ILP32'])
