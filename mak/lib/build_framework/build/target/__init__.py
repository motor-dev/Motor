import os
from .freebsd import setup_build_freebsd
from .linux import setup_build_linux
from .macos import setup_build_macos
from .solaris import setup_build_solaris
from .windows import setup_build_windows
from ...options import BuildContext

TARGETS = {
    'freebsd':
        setup_build_freebsd,
    'linux':
        setup_build_linux,
    'macos':
        setup_build_macos,
    'solaris':
        setup_build_solaris,
    'windows':
        setup_build_windows,
}


def _setup_build_extra(build_context: BuildContext) -> None:
    platform = build_context.env.VALID_PLATFORMS[0]
    build_context.recurse(
        os.path.join(
            build_context.motornode.abspath(),
            'extra',
            platform,
        ), 'build', once=False
    )


def setup_build_target(build_context: BuildContext) -> None:
    if build_context.env.VALID_PLATFORMS:
        platform = build_context.env.VALID_PLATFORMS[0]
        TARGETS.get(platform, _setup_build_extra)(build_context)
