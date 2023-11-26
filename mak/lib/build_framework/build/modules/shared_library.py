import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
from .module import module, preprocess, multiarch
from ...options import BuildContext
from typing import Optional, List, Union


def shared_library(
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
            depends=depends,
            uselib=uselib,
            conditions=conditions,
            extra_features=(not build_context.env.STATIC) and ['motor:module'] or []
        )
        return multiarch(
            build_context,
            name, [
                shared_library(
                    build_context, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in build_context.multiarch_envs
            ]
        )
    else:
        features = (features or []) + (
                build_context.env.STATIC and ['c', 'cxx', 'cxxobjects', 'motor:c', 'motor:cxx']
                or ['c', 'cxx', 'cxxshlib', 'motor:c', 'motor:cxx', 'motor:shared_lib']
        )
        return module(**locals())
