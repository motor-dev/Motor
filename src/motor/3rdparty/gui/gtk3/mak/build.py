import waflib.ConfigSet
import waflib.Node
import waflib.TaskGen
import build_framework
from typing import Optional


def build_source(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.headers(build_context, name, [], path=path, env=env)


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(
        build_context,
        name,
        var='gtk3',
        source_node=path,
        env=env,
        use=getattr(build_context, 'platforms'),
        feature_list=['gtk3'])


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(
        build_context,
        'motor.3rdparty.gui.gtk3',
        'GTK3_BINARY', build_binary,
        'GTK3_SOURCE', build_source
    )
