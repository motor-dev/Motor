import os
import waflib.Context
import waflib.Options
from typing import Optional
from ..options import SetupContext
from .package import pkg_unpack, multiarch_setup_package
from .checks import check_lib, check_header, check_package, check_framework, run_pkg_config, pkg_config, \
    multiarch_setup_checks
from .host import setup_host


def register_setup_option(setup_context: SetupContext, option_name: str) -> None:
    setup_context.env.append_value('SETUP_OPTIONS',
                                   [(option_name, getattr(waflib.Options.options, option_name))])


def start_msg_setup(setup_context: SetupContext,
                    third_party_name: Optional[str] = None) -> None:
    assert setup_context.path.parent is not None
    assert setup_context.path.parent.parent is not None
    setup_context.start_msg(
        '  %s.%s' % (
            setup_context.path.parent.parent.name,
            third_party_name if third_party_name is not None else setup_context.path.parent.name
        )
    )


def setup_framework(setup_context: SetupContext) -> None:
    """setup step before the build: recursively calls setup on every third party library"""
    setup_host(setup_context)
    env = setup_context.env
    extra = setup_context.motornode.make_node('extra')
    if env.VALID_PLATFORMS:
        extra_dir = os.path.join(extra.abspath(), env.VALID_PLATFORMS[0])
        if os.path.isdir(extra_dir):
            setup_context.recurse(extra_dir, once=False)


def multiarch_setup_framework(setup_context: SetupContext) -> None:
    multiarch_setup_checks(setup_context)
    multiarch_setup_package(setup_context)
    setup_context.fun = 'setup'
    if setup_context.env.SUB_TOOLCHAINS:
        for t in setup_context.env.SUB_TOOLCHAINS:
            try:
                setup_context.start_msg('Setting up environment')
                setup_context.end_msg(t)
                setup_context.setenv(t + '.setup', setup_context.all_envs[t])
                setup_context.env.TOOLCHAIN_NAME = setup_context.env.TOOLCHAIN
                setup_context.env.TOOLCHAIN = setup_context.env.TOOLCHAIN + '.setup'
                setup_context.recurse(waflib.Context.run_dir, once=False)
            except Exception:
                raise
            else:
                setup_context.env.MOTOR_SETUP = True
            finally:
                setup_context.variant = setup_context.motor_variant
        setup_context.setenv(
            setup_context.motor_variant + '.setup',
            setup_context.all_envs[setup_context.motor_variant]
        )
        setup_context.env.SUB_TOOLCHAINS = [t + '.setup' for t in setup_context.env.SUB_TOOLCHAINS]
        setup_context.env.MOTOR_SETUP = True
    else:
        t = setup_context.motor_variant
        try:
            setup_context.start_msg('Setting up environment')
            setup_context.end_msg(t)
            setup_context.setenv(t + '.setup', setup_context.all_envs[t])
            setup_context.env.TOOLCHAIN_NAME = setup_context.env.TOOLCHAIN
            setup_context.env.TOOLCHAIN = setup_context.env.TOOLCHAIN + '.setup'
            setup_context.recurse(waflib.Context.run_dir, once=False)
        except Exception:
            raise
        else:
            setup_context.env.MOTOR_SETUP = True
