from motor_typing import TYPE_CHECKING


def build(build_context):
    # type: (Build.BuildContext) -> None
    build_context.thirdparty('motor.3rdparty.graphics.DirectX12', var='dx12', feature_list=['DirectX12'])


if TYPE_CHECKING:
    from waflib import Build