import platform
import waflib.Options
from .darwin import options_host_darwin
from .freebsd import options_host_freebsd
from .linux import options_host_linux
from .sunos import options_host_sunos
from .windows import options_host_windows


def _options_host_unknown(_: waflib.Options.OptionsContext) -> None:
    pass


HOSTS = {
    'darwin': options_host_darwin,
    'freebsd': options_host_freebsd,
    'linux': options_host_linux,
    'sunos': options_host_sunos,
    'windows': options_host_windows,
}


def options_host(options_context: waflib.Options.OptionsContext) -> None:
    os_name = platform.uname()[0].lower().split('-')[0]
    HOSTS.get(os_name, _options_host_unknown)(options_context)
