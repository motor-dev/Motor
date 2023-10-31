import platform
import waflib.Build
import waflib.Errors
from .darwin import setup_host_darwin
from .freebsd import setup_host_freebsd
from .linux import setup_host_linux
from .sunos import setup_host_sunos
from .windows import setup_host_windows

SUPPORTED_OS = {
    'darwin':
        setup_host_darwin,
    'freebsd':
        setup_host_freebsd,
    'linux':
        setup_host_linux,
    'sunos':
        setup_host_sunos,
    'windows':
        setup_host_windows,
}


def _setup_unknown_host(_: waflib.Build.BuildContext) -> None:
    pass
    # raise waflib.Errors.WafError("Unsupported host {}".format(platform.uname()))


def setup_build_host(build_context: waflib.Build.BuildContext) -> None:
    os_name = platform.uname()[0].lower().split('-')[0]
    SUPPORTED_OS.get(os_name, _setup_unknown_host)(build_context)
