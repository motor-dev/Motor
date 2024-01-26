from ....options import ConfigurationContext
from . import (
    amd64,
    arm64,
    arm64_32,
    arm64e,
    powerpc64,
    powerpc64le,
)

ARCHS = {
    'aarch64': arm64.configure,
    'aarch64_32': arm64_32.configure,
    'amd64': amd64.configure,
    'arm64': arm64.configure,
    'arm64_32': arm64_32.configure,
    'arm64e': arm64e.configure,
    'powerpc64': powerpc64.configure,
    'powerpc64le': powerpc64le.configure,
    'ppc64': powerpc64.configure,
    'ppc64le': powerpc64le.configure,
    'x64': amd64.configure,
    'x86_64': amd64.configure
}


def setup_arch(configuration_context: ConfigurationContext) -> None:
    ARCHS[configuration_context.env.ARCH_NAME](configuration_context)
    configuration_context.common_env.append_unique('ALL_ARCHS', list(ARCHS.keys()))
