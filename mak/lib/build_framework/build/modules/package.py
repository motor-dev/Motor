import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
from .module import preprocess, multiarch
from ...options import BuildContext
from typing import Callable, Optional


def package(
        build_context: BuildContext,
        name: str,
        system_var: str,
        binary_build: Callable[[BuildContext, str, waflib.ConfigSet.ConfigSet,
                                waflib.Node.Node], Optional[waflib.TaskGen.task_gen]],
        source_var: str,
        source_build: Callable[[BuildContext, str, waflib.ConfigSet.ConfigSet,
                                waflib.Node.Node], Optional[waflib.TaskGen.task_gen]]
) -> None:
    arch_list = []
    pp = None
    for env in build_context.multiarch_envs:
        pkg_path = env[system_var]
        if not pkg_path or env.PROJECTS:
            if env[source_var]:
                path = build_context.package_node.make_node(env[source_var])
                if pp is None:
                    pp = preprocess(
                        build_context,
                        name,
                        path,
                        '',
                        name,
                        [],
                        [],
                        extra_features=['motor:deploy:off']
                    )
                arch_list.append(source_build(build_context, name, env, path))
        else:
            if not isinstance(pkg_path, bool):
                path = build_context.package_node.make_node(pkg_path)
            else:
                path = build_context.path.parent
            arch_list.append(binary_build(build_context, name, env, path))
    if arch_list:
        multiarch(build_context, name, arch_list)
