import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
from .module import module, preprocess, multiarch
from ...options import BuildContext
from typing import Optional, List, Union


def headers(
        build_context: BuildContext,
        name: str,
        depends: Optional[List[str]] = None,
        private_depends: Optional[List[str]] = None,
        path: Optional[waflib.Node.Node] = None,
        features: Optional[List[str]] = None,
        extra_includes: Optional[List[waflib.Node.Node]] = None,
        extra_defines: Optional[List[str]] = None,
        extra_public_includes: Optional[List[waflib.Node.Node]] = None,
        extra_system_includes: Optional[List[Union[waflib.Node.Node, str]]] = None,
        extra_public_defines: Optional[List[str]] = None,
        uselib: Optional[List[str]] = None,
        source_list: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None,
        root_namespace: str = 'Motor',
        project_name: Optional[str] = None,
        env: Optional[waflib.ConfigSet.ConfigSet] = None
) -> Optional[waflib.TaskGen.task_gen]:
    if env is None:
        preprocess(
            build_context,
            name,
            path,
            root_namespace,
            'motor',
            depends,
            uselib,
            conditions,
            [])
        return multiarch(
            build_context,
            name, [
                headers(
                    build_context, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in build_context.multiarch_envs
            ]
        )
    else:
        features = (features or []) + ['c', 'cxx', 'motor:c', 'motor:cxx']
        return module(**locals())
