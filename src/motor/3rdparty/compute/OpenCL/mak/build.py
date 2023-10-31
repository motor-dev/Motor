import build_framework
import waflib.ConfigSet
import waflib.Node
import waflib.TaskGen


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> waflib.TaskGen.task_gen:
    tg = build_framework.thirdparty(
        build_context,
        name,
        source_node=path,
        feature_list=['OpenCL'],
        use=['motor.3rdparty.graphics.OpenGL'],
        env=env,
    )
    assert tg is not None
    setattr(tg, 'export_includes', [build_context.path.parent.find_node('api')])
    return tg


def build_project(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> waflib.TaskGen.task_gen:
    tg = build_framework.thirdparty(
        build_context,
        name,
        source_node=path,
        feature_list=['OpenCL'],
        use=['motor.3rdparty.graphics.OpenGL'],
        env=env,
    )
    assert tg is not None
    setattr(tg, 'export_includes', [build_context.path.parent.find_node('api')])
    return tg


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(build_context, 'motor.3rdparty.compute.OpenCL', 'OPENCL_BINARY', build_binary,
                            'OPENCL_SOURCE',
                            build_project)
