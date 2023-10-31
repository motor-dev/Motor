import build_framework


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.thirdparty(build_context, 'motor.3rdparty.system.dbghelp')
