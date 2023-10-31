import build_framework


def build(build_context: build_framework.BuildContext) -> None:
    if build_context.env.TCLTK_BINARY:
        build_framework.thirdparty(
            build_context,
            'motor.3rdparty.scripting.tcltk',
            source_node=build_context.package_node.make_node(build_context.env.TCLTK_BINARY),
        )
