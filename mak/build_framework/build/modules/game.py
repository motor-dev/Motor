from waflib.Configure import conf


@conf
def game(
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
        bld.preprocess(name, path, root_namespace, name, uselib=uselib)
        bld.multiarch(
            name, [
                game(
                    bld, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, uselib, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in bld.multiarch_envs
            ]
        )
    else:
        features = features + [
            'c', 'cxx', bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:c', 'motor:cxx', 'motor:plugin',
            'motor:game'
        ]
        return bld.module(**locals())


def build(build_context):
    pass