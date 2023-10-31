from ....options import ConfigurationContext


def configure(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ARCHITECTURE = 'x86_64'
    configuration_context.env.VALID_ARCHITECTURES = ['amd64', 'x64', 'x86_64']
    configuration_context.env.ARCH_FAMILY = 'x86'
    configuration_context.env.ARCH_LP64 = True
    configuration_context.env.append_unique('DEFINES', ['_AMD64', '_LP64'])
