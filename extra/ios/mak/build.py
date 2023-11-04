import os
import build_framework
import build_framework.build.target.macos
import waflib.TaskGen


def build(build_context: build_framework.BuildContext) -> None:
    if not build_context.env.PROJECTS:
        build_framework.build.target.macos.setup_build_macos(build_context)
