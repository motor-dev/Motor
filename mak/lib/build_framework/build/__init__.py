import os
import sys
import waflib.Build
import waflib.Errors
import waflib.Node
import waflib.Options
import waflib.TaskGen
from ..options import BuildContext
from .modules import *
from .features import create_compiled_task, make_bld_node, apply_source_filter
from .host import setup_build_host
from .target import setup_build_target
from .compiler import setup_build_compiler
from .display import setup_display
from .unit_test import setup_unit_test
from .masterfiles import setup_masterfiles as _setup_masterfiles
from .strip import create_strip_task
from .install import install_directory, install_files, install_as


def build_framework(build_context: BuildContext) -> None:
    setup_display(build_context)
    if getattr(build_context, 'motor_variant', None) is None:
        raise waflib.Errors.WafError(
            'Call %s %s %s:toolchain:variant\n'
            '  (with toolchain in:\n    %s)\n  (with variant in:\n    %s)' % (
                sys.executable, sys.argv[0], build_context.cmd, '\n    '.join(build_context.env.ALL_TOOLCHAINS
                                                                              ),
                '\n    '.join(build_context.env.ALL_VARIANTS)
            )
        )
    build_context.env = build_context.all_envs[build_context.motor_variant]
    build_context.package_env = build_context.all_envs['packages']
    build_context.package_node = build_context.root.make_node(build_context.out_dir)
    build_context.package_node = build_context.package_node.make_node('packages')
    build_context.platforms = []

    tool_dir = os.path.join(build_context.motornode.abspath(), 'mak', 'lib', 'waftools')
    build_context.load('cpp_parser', tooldir=[tool_dir])
    build_context.load('metagen', tooldir=[tool_dir])
    build_context.load('kernel', tooldir=[tool_dir])
    build_context.load('bin2c', tooldir=[tool_dir])
    build_context.load('clir', tooldir=[tool_dir])
    build_context.load('ir_compiler', tooldir=[tool_dir])
    build_context.load('cmake', tooldir=[tool_dir])
    build_context.env.STATIC = build_context.env.STATIC or waflib.Options.options.static
    build_context.env.DYNAMIC = waflib.Options.options.dynamic
    if build_context.env.STATIC and build_context.env.DYNAMIC:
        raise waflib.Errors.WafError('--static and --dynamic are mutually exclusive.')
    build_context.common_env = build_context.env

    setup_build_host(build_context)
    setup_unit_test(build_context)
    for env_name in build_context.env.SUB_TOOLCHAINS:
        build_context.common_env.append_unique('VALID_PLATFORMS', build_context.all_envs[env_name].VALID_PLATFORMS)
    build_context.multiarch_envs = [build_context.all_envs[envname] for envname in
                                    sorted(build_context.env.SUB_TOOLCHAINS)] or [build_context.env]
    setup_build_target(build_context)
    setup_build_compiler(build_context)

    if build_context.env.PROJECTS:

        def rc_hook(_: waflib.TaskGen.task_gen, __: waflib.Node.Node) -> None:
            """creates RC hook to silence waf error"""
            pass

        if '.rc' not in waflib.TaskGen.task_gen.mappings:
            waflib.TaskGen.task_gen.mappings['.rc'] = rc_hook

    _setup_masterfiles(build_context)
