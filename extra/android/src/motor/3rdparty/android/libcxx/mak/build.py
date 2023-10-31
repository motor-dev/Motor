import build_framework
import waflib.ConfigSet
import waflib.Node
import waflib.TaskGen
from typing import Optional


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(build_context, name, source_node=path, env=env)


def build_source(
        _: build_framework.BuildContext,
        __: str,
        ___: waflib.ConfigSet.ConfigSet,
        ____: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    raise NotImplementedError


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(build_context, 'motor.3rdparty.android.libcxx', 'LIBCPP_BINARY', build_binary,
                            'LIBCPP_SOURCE', build_source)
