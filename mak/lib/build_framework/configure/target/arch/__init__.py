from ....options import ConfigurationContext
from . import (
    aarch32,
    amd64,
    arm,
    arm64,
    arm64_32,
    arm64e,
    armv6,
    armv7,
    armv7a,
    armv7k,
    armv7s,
    ia64,
    powerpc,
    powerpc64,
    powerpc64le,
    x86,
)

ARCHS = {
    'aarch32': aarch32.configure,
    'aarch64': arm64.configure,
    'aarch64_32': arm64_32.configure,
    'amd64': amd64.configure,
    'arm': arm.configure,
    'arm64': arm64.configure,
    'arm64_32': arm64_32.configure,
    'arm64e': arm64e.configure,
    'armv6': armv6.configure,
    'armv7': armv7.configure,
    'armv7a': armv7a.configure,
    'armv7k': armv7k.configure,
    'armv7s': armv7s.configure,
    'i386': x86.configure,
    'ia64': ia64.configure,
    'powerpc': powerpc.configure,
    'powerpc64': powerpc64.configure,
    'powerpc64le': powerpc64le.configure,
    'ppc': powerpc.configure,
    'ppc64': powerpc64.configure,
    'ppc64le': powerpc64le.configure,
    'x64': amd64.configure,
    'x86': x86.configure,
    'x86_64': amd64.configure
}


def setup_arch(configuration_context: ConfigurationContext) -> None:
    ARCHS[configuration_context.env.ARCH_NAME](configuration_context)
    configuration_context.common_env.append_unique('ALL_ARCHS', list(ARCHS.keys()))
