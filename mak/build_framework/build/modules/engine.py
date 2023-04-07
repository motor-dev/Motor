from waflib.Configure import conf
from waflib import Errors


@conf
def engine(
    bld,
    name,
    depends=[],
    private_depends=[],
    path=None,
    features=[],
    extra_includes=[],
    extra_defines=[],
    extra_public_includes=[],
    extra_system_includes=[],
    extra_public_defines=[],
    uselib=[],
    source_list=None,
    conditions=[],
    root_namespace='Motor',
    project_name=None,
    env=None
):
    if env is None:
        if getattr(bld, 'launcher', None) != None:
            raise Errors.WafError('Only one engine launcher can be defined')
        p = bld.preprocess(
            name, path, root_namespace, 'motor', depends=depends, uselib=uselib, extra_features=['motor:module']
        )
        bld.launcher = bld.multiarch(
            name, [
                engine(
                    bld, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in bld.multiarch_envs
            ]
        )
        if 'windows' in bld.env.VALID_PLATFORMS:
            if project_name is not None:
                project_name = project_name + '.console'
            bld.preprocess(
                name + '.console',
                p.source_nodes[0],
                root_namespace,
                'motor',
                depends=depends,
                uselib=uselib,
                extra_features=['motor:module']
            )
            bld.multiarch(
                name + '.console', [
                    engine(
                        bld, name + '.console', depends, private_depends + ['console'], p.source_nodes[0], features,
                        extra_includes, extra_defines, extra_public_includes, extra_system_includes,
                        extra_public_defines, uselib, source_list, conditions, root_namespace, project_name, env
                    ) for env in bld.multiarch_envs
                ]
            )
        return bld.launcher
    else:
        features = features + ['c', 'cxx', 'cxxprogram', 'motor:c', 'motor:cxx', 'motor:launcher']
        return bld.module(**locals())


def build(build_context):
    pass
