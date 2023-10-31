import os
import waflib.Configure
import waflib.Options
import waflib.Logs
from typing import List
from ...options import ConfigurationContext
from .platform import Platform
from .freebsd import configure_target_freebsd
from .linux import configure_target_linux
from .macos import configure_target_macos
from .solaris import configure_target_solaris
from .windows import configure_target_windows
from .compiler import configure_compiler


def configure_target(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.ALL_VARIANTS = ['debug', 'profile', 'final']
    platforms = waflib.Options.options.platforms
    platforms = platforms.split(',') if platforms else []

    Platform.platforms = []

    if not platforms or 'freebsd' in platforms:
        configure_target_freebsd(configuration_context, Platform.platforms)
    if not platforms or 'linux' in platforms:
        configure_target_linux(configuration_context, Platform.platforms)
    if not platforms or 'macos' in platforms:
        configure_target_macos(configuration_context, Platform.platforms)
    if not platforms or 'solaris' in platforms:
        configure_target_solaris(configuration_context, Platform.platforms)
    if not platforms or 'windows' in platforms:
        configure_target_windows(configuration_context, Platform.platforms)

    for extra in configuration_context.motornode.make_node('extra').listdir():
        if os.path.isfile(os.path.join(configuration_context.motornode.abspath(), 'extra', extra, 'wscript')):
            if not platforms or extra in platforms:
                configuration_context.recurse(os.path.join(configuration_context.motornode.abspath(), 'extra', extra))

    compilers = configure_compiler(configuration_context)
    setattr(configuration_context, 'compilers', compilers)

    for p in Platform.platforms:
        configuration_list = p.get_available_compilers(configuration_context, compilers)
        if configuration_list:
            waflib.Logs.pprint('BLUE', ' + configuring for platform %s' % p.NAME)
            for main_toolchain, sub_toolchains, target_platform in configuration_list:
                target_platform.add_toolchain(configuration_context, main_toolchain, sub_toolchains)
    configuration_context.env.store('./.waf_toolchains.cache')
