import build_framework


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.static_library(build_context, 'motor.3rdparty.android.libklcompat', path=build_context.path.parent)
