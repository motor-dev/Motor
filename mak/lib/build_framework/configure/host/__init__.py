import platform
import waflib.Configure
from .darwin import configure_host_darwin
from .freebsd import configure_host_freebsd
from .linux import configure_host_linux
from .sunos import configure_host_sunos
from .windows import configure_host_windows


def _configure_host_unknown(_: waflib.Configure.ConfigurationContext) -> None:
    pass


HOSTS = {
    'darwin': configure_host_darwin,
    'freebsd': configure_host_freebsd,
    'linux': configure_host_linux,
    'sunos': configure_host_sunos,
    'windows': configure_host_windows,
}


def configure_host(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    os_name = platform.uname()[0].lower().split('-')[0]
    configuration_context.env.HOST = os_name
    HOSTS.get(os_name, _configure_host_unknown)(configuration_context)
