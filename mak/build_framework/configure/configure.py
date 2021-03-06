import os
from motor_typing import TYPE_CHECKING


def configure(configuration_context):
    # type: (Configure.ConfigurationContext) -> None
    "Recursively calls configure on host and all targets to create all available toolchains"
    configuration_context.recurse('host/host.py')
    extra = configuration_context.motornode.make_node('extra')
    for extra_platform in extra.listdir():
        directory = extra.make_node(extra_platform).abspath()
        if os.path.isdir(directory) and os.path.isfile(os.path.join(directory, 'wscript')):
            configuration_context.recurse(extra.make_node(extra_platform).abspath(), name='host_configure')
    tool_dir = os.path.join(configuration_context.motornode.abspath(), 'mak', 'tools')

    configuration_context.setenv('projects', configuration_context.env.derive())
    configuration_context.env.TOOLCHAIN = 'projects'
    configuration_context.env.PROJECTS = True
    configuration_context.env.ENV_PREFIX = '%s'
    configuration_context.env.SUBARCH = False
    configuration_context.variant = ''

    configuration_context.load('flex', tooldir=[tool_dir])
    configuration_context.load('bison', tooldir=[tool_dir])
    configuration_context.recurse('sysroot.py')
    configuration_context.recurse('compiler/compiler.py')
    configuration_context.load('clir', tooldir=[tool_dir])
    configuration_context.recurse('target/target.py')
    configuration_context.recurse('package.py')
    configuration_context.env.ALL_TOOLCHAINS.sort(key=lambda x: x.split('-'))


if TYPE_CHECKING:
    from waflib import Configure