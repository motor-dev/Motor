import os
import sys
from motor_typing import TYPE_CHECKING
from waflib import Options, Configure, Logs


@Configure.conf
def register_setup_option(configuration_context, option_name):
    # type: (Configure.ConfigurationContext, str) -> None
    configuration_context.env.append_value('SETUP_OPTIONS', [(option_name, getattr(Options.options, option_name))])


@Configure.conf
def start_msg_setup(configuration_context, third_party_name=None):
    # type: (Configure.ConfigurationContext, Optional[str]) -> None
    configuration_context.start_msg(
        '  %s.%s' % (
            configuration_context.path.parent.parent.name,
            third_party_name if third_party_name is not None else configuration_context.path.parent.name
        )
    )


def setup(configuration_context):
    # type: (Configure.ConfigurationContext) -> None
    "setup step before the build: recursively calls setup on every third party library"
    configuration_context.recurse('host/host.py')
    extra = configuration_context.motornode.make_node('extra')
    if configuration_context.env.VALID_PLATFORMS:
        extra_dir = os.path.join(extra.abspath(), configuration_context.env.VALID_PLATFORMS[0])
        if os.path.isdir(extra_dir):
            configuration_context.recurse(extra_dir, once=False)


def multiarch_setup(configuration_context):
    # type: (Configure.ConfigurationContext) -> None
    configuration_context.recurse('checks.py')
    configuration_context.recurse('package.py')
    configuration_context.fun = 'setup'
    if configuration_context.env.SUB_TOOLCHAINS:
        for t in configuration_context.env.SUB_TOOLCHAINS:
            if Options.options.progress_bar == 1 and sys.stdout.isatty():
                configuration_context.in_msg = True
                pprint = Logs.pprint
                Logs.pprint = lambda *k, **kw: None
            try:
                configuration_context.start_msg('Setting up environment')
                configuration_context.end_msg(t)
                configuration_context.setenv(t + '.setup', configuration_context.all_envs[t])
                configuration_context.env.TOOLCHAIN = configuration_context.env.TOOLCHAIN + '.setup'
                configuration_context.recurse(configuration_context.run_dir, once=False)
            except Exception as e:
                raise
            else:
                configuration_context.env.MOTOR_SETUP = True
            finally:
                configuration_context.variant = configuration_context.motor_variant
                if Options.options.progress_bar == 1 and sys.stdout.isatty():
                    configuration_context.in_msg = False
                    Logs.pprint = pprint
        configuration_context.setenv(
            configuration_context.motor_variant + '.setup',
            configuration_context.all_envs[configuration_context.motor_variant]
        )
        configuration_context.env.SUB_TOOLCHAINS = [t + '.setup' for t in configuration_context.env.SUB_TOOLCHAINS]
        configuration_context.env.MOTOR_SETUP = True
    else:
        t = configuration_context.motor_variant
        if Options.options.progress_bar == 1 and sys.stdout.isatty():
            configuration_context.in_msg = True
            pprint = Logs.pprint
            Logs.pprint = lambda *k, **kw: None
        try:
            configuration_context.start_msg('Setting up environment')
            configuration_context.end_msg(t)
            configuration_context.setenv(t + '.setup', configuration_context.all_envs[t])
            configuration_context.env.TOOLCHAIN = configuration_context.env.TOOLCHAIN + '.setup'
            configuration_context.recurse(configuration_context.run_dir, once=False)
        except Exception as e:
            raise
        else:
            configuration_context.env.MOTOR_SETUP = True
        finally:
            if Options.options.progress_bar == 1 and sys.stdout.isatty():
                configuration_context.in_msg = False
                Logs.pprint = pprint


if TYPE_CHECKING:
    from waflib import Configure
    from typing import Optional
