import os
from ..options import ConfigurationContext
from .package import configure_package
from .sysroot import configure_sysroot
from .host import configure_host
from .target import configure_target


def configure_framework(configuration_context: ConfigurationContext) -> None:
    """Recursively calls configure on host and all targets to create all available toolchains"""
    configure_host(configuration_context)
    extra = configuration_context.motornode.make_node('extra')
    for extra_platform in extra.listdir():
        directory = extra.make_node(extra_platform).abspath()
        if os.path.isdir(directory) and os.path.isfile(os.path.join(directory, 'wscript')):
            configuration_context.recurse(extra.make_node(extra_platform).abspath(), name='host_configure')
    tool_dir = os.path.join(configuration_context.motornode.abspath(), 'mak', 'lib', 'waftools')

    configuration_context.setenv('projects', configuration_context.env.derive())
    configuration_context.env.TOOLCHAIN = 'projects'
    configuration_context.env.PROJECTS = True
    configuration_context.env.ENV_PREFIX = '%s'
    configuration_context.env.SUBARCH = False
    configuration_context.variant = ''

    configuration_context.load(['flex'], tooldir=[tool_dir])
    configuration_context.load(['bison'], tooldir=[tool_dir])
    configure_sysroot(configuration_context)
    configure_target(configuration_context)
    configuration_context.load(['clir'], tooldir=[tool_dir])
    configure_package(configuration_context)
    configuration_context.env.ALL_TOOLCHAINS.sort(key=lambda x: x.split('-'))
