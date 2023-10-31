import platform
from ...options import SetupContext
from .darwin import setup_host_darwin
from .freebsd import setup_host_freebsd
from .linux import setup_host_linux
from .sunos import setup_host_sunos
from .windows import setup_host_windows


def _setup_host_unknown(_: SetupContext) -> None:
    pass


HOSTS = {
    'darwin': setup_host_darwin,
    'freebsd': setup_host_freebsd,
    'linux': setup_host_linux,
    'sunos': setup_host_sunos,
    'windows': setup_host_windows,
}


def setup_host(setup_context: SetupContext) -> None:
    os_name = platform.uname()[0].lower().split('-')[0]
    setup_context.env.HOST = os_name
    HOSTS.get(os_name, _setup_host_unknown)(setup_context)
