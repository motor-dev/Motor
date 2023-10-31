#! /usr/bin/env python
"""
    Main wscript for the Motor engine
"""

VERSION = "0.2.0"
APPNAME = "Motor"

top = '.'  # pylint: disable=invalid-name
out = 'bld/.waf'  # pylint: disable=invalid-name

import build_framework


def options(options_context: build_framework.OptionsContext) -> None:
    """recursively declare options to the parser"""
    setattr(options_context, 'motornode', options_context.path)
    build_framework.options_framework(options_context)
    options_context.recurse('src/options.py')


def configure(configuration_context: build_framework.ConfigurationContext) -> None:
    """entry point for build system configuration"""
    configuration_context.motornode = configuration_context.path
    build_framework.configure_framework(configuration_context)
    configuration_context.recurse('src/configure.py')


def multiarch_setup(setup_context: build_framework.SetupContext) -> None:
    """setup a set of toolchains in a multi-arch environment (e.g. Android, MacOS)"""
    setup_context.motornode = setup_context.path
    build_framework.multiarch_setup_framework(setup_context)


def setup(setup_context: build_framework.SetupContext) -> None:
    """setup a platform environment in the current configuration context"""
    setup_context.motornode = setup_context.path
    build_framework.setup_framework(setup_context)
    setup_context.recurse('src/setup.py', once=False)


def build(build_context: build_framework.BuildContext) -> None:
    """set up build targets and executes the build"""
    build_context.motornode = build_context.path
    build_framework.build_framework(build_context)
    build_context.recurse('src/build.py')
