from waflib.Configure import conf


@conf
def headers(
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
    source_list=None,
    conditions=[],
    root_namespace='Motor',
    project_name=None,
    env=None
):
    if env is None:
        bld.preprocess(name, path, root_namespace, 'motor')
        bld.multiarch(
            name, [
                headers(
                    bld, name, depends, private_depends, path, features, extra_includes, extra_defines,
                    extra_public_includes, extra_system_includes, extra_public_defines, source_list, conditions,
                    root_namespace, project_name, env
                ) for env in bld.multiarch_envs
            ]
        )
    else:
        features = features + ['c', 'cxx', 'motor:c', 'motor:cxx']
        return bld.module(**locals())


def build(build_context):
    pass