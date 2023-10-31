import build_framework


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.thirdparty(build_context, 'motor.3rdparty.graphics.DirectX12', var='dx12',
                               feature_list=['DirectX12'])
