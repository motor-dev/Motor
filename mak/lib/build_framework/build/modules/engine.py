import waflib.Errors
import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
from .module import module, preprocess, multiarch
from ...options import BuildContext
from typing import Optional, List, Union


def engine(
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
        if build_context.launcher is not None:
            raise waflib.Errors.WafError('Only one engine launcher can be defined')
        p = preprocess(
            build_context,
            name,
            path,
            root_namespace,
            'motor',
            depends=depends,
            uselib=uselib,
            extra_features=['motor:module']
        )
        build_context.launcher = multiarch(
            build_context,
            name, [
                engine(
                    build_context, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in build_context.multiarch_envs
            ]
        )
        if 'windows' in build_context.env.VALID_PLATFORMS:
            if project_name is not None:
                project_name = project_name + '.console'
            preprocess(
                build_context,
                name + '.console',
                getattr(p, 'source_nodes')[0][1],
                root_namespace,
                'motor',
                depends=depends,
                uselib=uselib,
                extra_features=['motor:module']
            )
            multiarch(
                build_context,
                name + '.console', [
                    engine(
                        build_context, name + '.console', depends, (private_depends or []) + ['console'],
                        getattr(p, 'source_nodes')[0][1],
                        features,
                        extra_includes, extra_defines, extra_public_includes, extra_system_includes,
                        extra_public_defines, uselib, source_list, conditions, root_namespace, project_name, env
                    ) for env in build_context.multiarch_envs
                ]
            )
        return build_context.launcher
    else:
        features = (features or []) + ['c', 'cxx', 'cxxprogram', 'motor:c', 'motor:cxx', 'motor:launcher']
        return module(**locals())
