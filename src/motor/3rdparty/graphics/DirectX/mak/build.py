from motor_typing import TYPE_CHECKING


def build(build_context):
    # type: (Build.BuildContext) -> None
    build_context.thirdparty('motor.3rdparty.graphics.DirectX9', var='dx9', feature_list=['DirectX9'])
    build_context.thirdparty('motor.3rdparty.graphics.DirectX10', var='dx10', feature_list=['DirectX10'])
    build_context.thirdparty('motor.3rdparty.graphics.DirectX11', var='dx11', feature_list=['DirectX11'])


if TYPE_CHECKING:
    from waflib import Build