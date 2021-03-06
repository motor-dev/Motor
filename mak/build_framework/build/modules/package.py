from waflib.Configure import conf


@conf
def package(build_context, name, system_var, binary_build, source_var, source_build):
    arch_list = []
    preprocess = None
    for env in build_context.multiarch_envs:
        pkg_path = env[system_var]
        if not pkg_path or env.PROJECTS:
            if env[source_var]:
                path = build_context.package_node.make_node(env[source_var])
                if not preprocess:
                    preprocess = build_context.preprocess(name, path, '', name, [], extra_features=['motor:deploy:off'])
                arch_list.append(source_build(build_context, name, env, path))
        else:
            if not isinstance(pkg_path, bool):
                path = build_context.package_node.make_node(pkg_path)
            else:
                path = build_context.path.parent
            arch_list.append(binary_build(build_context, name, env, path))
    if arch_list:
        build_context.multiarch(name, arch_list)


def build(build_context):
    pass