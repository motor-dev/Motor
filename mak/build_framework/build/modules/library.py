from waflib.Configure import conf


@conf
def library(
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
        bld.preprocess(
            name,
            path,
            root_namespace,
            'motor',
            depends=depends,
            uselib=uselib,
            extra_features=bld.env.DYNAMIC and ['motor:module'] or []
        )
        bld.multiarch(
            name, [
                library(
                    bld, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in bld.multiarch_envs
            ]
        )
    else:
        features = features + (
            bld.env.DYNAMIC and ['c', 'cxx', 'cxxshlib', 'motor:c', 'motor:cxx', 'motor:shared_lib']
            or ['c', 'cxx', 'cxxobjects', 'motor:c', 'motor:cxx']
        )
        return bld.module(**locals())


def build(build_context):
    pass