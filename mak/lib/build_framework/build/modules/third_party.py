import os
import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
from ..install import install_directory
from ...options import BuildContext
from typing import Optional, List


def add_feature(self: BuildContext, feature: str,
                env: Optional[waflib.ConfigSet.ConfigSet] = None) -> None:
    if env:
        env.append_unique('FEATURES', feature)
    else:
        for multiarch_env in self.multiarch_envs:
            multiarch_env.append_unique('FEATURES', feature)


def expand_libpath(build_context: BuildContext, libpath: List[str]) -> List[str]:
    result = []
    for path in libpath:
        if os.path.isdir(os.path.join(path, build_context.env.OPTIM)):
            result.append(os.path.join(path, build_context.env.OPTIM))
        else:
            result.append(path)
    return result


def expand_nodepath(build_context: BuildContext, nodepath: List[waflib.Node.Node]) \
        -> List[waflib.Node.Node]:
    result = []
    for n in nodepath:
        if n.make_node(build_context.env.OPTIM).isdir():
            result.append(n.make_node(build_context.env.OPTIM))
        else:
            result.append(n)
    return result


def thirdparty(
        build_context: BuildContext,
        name: str,
        feature_list: Optional[List[str]] = None,
        path: str = '',
        source_node: Optional[waflib.Node.Node] = None,
        var: str = '',
        use: Optional[List[str]] = None,
        private_use: Optional[List[str]] = None, env: Optional[waflib.ConfigSet.ConfigSet] = None
) -> Optional[waflib.TaskGen.task_gen]:
    var = var or build_context.path.parent.name
    feature_list = feature_list or []
    use = use or []
    private_use = private_use or []
    platforms = build_context.env.VALID_PLATFORMS
    platform_specific = platforms
    if source_node is None:
        source_node = build_context.path.parent.make_node(path and path.replace('.', '/') or '.')
    if env is None:
        internal_deps = []
        tg = None
        for env in build_context.multiarch_envs:
            target_name = env.ENV_PREFIX % name
            if env['check_%s' % var] or env.PROJECTS:
                for feature in feature_list:
                    add_feature(build_context, feature, env)
                var_id = var.upper().replace('+', 'P').replace('-', '_')
                tg = build_context(
                    group=build_context.motor_variant,
                    target=target_name,
                    features=['c', 'cxx'],
                    export_includes=env['check_%s_includes' % var],
                    export_defines=env['check_%s_defines' % var] + ['MOTOR_HAVE_%s' % var_id],
                    export_libpath=expand_libpath(build_context, env['check_%s_libpath' % var]),
                    export_stlibpath=expand_libpath(build_context, env['check_%s_stlibpath' % var]),
                    export_lib=env['check_%s_libs' % var],
                    export_framework=env['check_%s_frameworks' % var],
                    export_cflags=env['check_%s_cflags' % var],
                    export_cxxflags=env['check_%s_cxxflags' % var],
                    export_linkflags=env['check_%s_ldflags' % var],
                    source_nodes=[('', source_node)],
                    use=[env.ENV_PREFIX % u for u in use],
                    private_use=[env.ENV_PREFIX % u for u in private_use],
                    project_name=name
                )
                if env.SUBARCH:
                    internal_deps.append(tg)
                archs = env.VALID_ARCHITECTURES
                arch_specific = archs + ['%s.%s' % (p, a) for p in platforms for a in archs]
                bin_paths = [
                    i for i in [source_node.make_node('bin.%s' % arch) for arch in arch_specific]
                    if os.path.isdir(i.abspath())
                ]
                data_paths = [
                    i for i in [source_node.make_node('data.%s' % arch) for arch in arch_specific]
                    if os.path.isdir(i.abspath())
                ]
                for bin_path in bin_paths:
                    install_directory(tg, env, bin_path, '', 'DEPLOY_RUNBINDIR')
                for data_path in data_paths:
                    install_directory(tg, env, data_path, '', 'DEPLOY_DATADIR')
                if name not in build_context.env.THIRDPARTIES_FIRST:
                    bin_paths = [
                        i for i in [source_node.make_node('bin')] +
                                   [source_node.make_node('bin.%s' % platform) for platform in platform_specific]
                        if os.path.isdir(i.abspath())
                    ]
                    data_paths = [
                        i for i in [source_node.make_node('data')] +
                                   [source_node.make_node('data.%s' % platform) for platform in platform_specific]
                        if os.path.isdir(i.abspath())
                    ]
                    for bin_path in bin_paths:
                        install_directory(tg, env, bin_path, '', 'DEPLOY_RUNBINDIR')
                    for data_path in data_paths:
                        install_directory(tg, env, data_path, '', 'DEPLOY_DATADIR')
                    build_context.env.append_unique('THIRDPARTIES_FIRST', name)

        if tg is not None:
            if internal_deps:
                tg = build_context(
                    group=build_context.motor_variant,
                    target=name,
                    features=['motor:multiarch'],
                    use=[d.name for d in internal_deps]
                )

            if name not in build_context.env.THIRDPARTIES_FIRST:
                bin_paths = [
                    i for i in [source_node.make_node('bin')] +
                               [source_node.make_node('bin.%s' % platform) for platform in platform_specific]
                    if os.path.isdir(i.abspath())
                ]
                data_paths = [
                    i for i in [source_node.make_node('data')] +
                               [source_node.make_node('data.%s' % platform) for platform in platform_specific]
                    if os.path.isdir(i.abspath())
                ]
                for bin_path in bin_paths:
                    install_directory(tg, build_context.env, bin_path, '', 'DEPLOY_RUNBINDIR')
                for data_path in data_paths:
                    install_directory(tg, env, data_path, '', 'DEPLOY_DATADIR')
                build_context.env.append_unique('THIRDPARTIES_FIRST', name)
            return tg
        else:
            return None
    else:
        target_name = env.ENV_PREFIX % name
        if env['check_%s' % var] or env.PROJECTS:
            for feature in feature_list:
                add_feature(build_context, feature, env)
            var_id = var.upper().replace('+', 'P').replace('-', '_')
            tg = build_context(
                group=build_context.motor_variant,
                target=target_name,
                features=['c', 'cxx'],
                export_includes=env['check_%s_includes' % var],
                export_defines=env['check_%s_defines' % var] + ['MOTOR_HAVE_%s' % var_id],
                export_libpath=expand_libpath(build_context, env['check_%s_libpath' % var]),
                export_stlibpath=expand_libpath(build_context, env['check_%s_stlibpath' % var]),
                export_lib=env['check_%s_libs' % var],
                export_framework=env['check_%s_frameworks' % var],
                export_cflags=env['check_%s_cflags' % var],
                export_cxxflags=env['check_%s_cxxflags' % var],
                export_linkflags=env['check_%s_ldflags' % var],
                source_nodes=[('', source_node)],
                use=[env.ENV_PREFIX % u for u in use],
                private_use=[env.ENV_PREFIX % u for u in private_use],
                project_name=name
            )
            archs = env.VALID_ARCHITECTURES
            arch_specific = archs + ['%s.%s' % (p, a) for p in platforms for a in archs]
            bin_paths = expand_nodepath(
                build_context, [
                    i for i in [source_node.make_node('bin.%s' % arch)
                                for arch in arch_specific] if os.path.isdir(i.abspath())
                ]
            )
            data_paths = [
                i for i in [source_node.make_node('data.%s' % arch) for arch in arch_specific]
                if os.path.isdir(i.abspath())
            ]
            for bin_path in bin_paths:
                install_directory(tg, env, bin_path, '', 'DEPLOY_RUNBINDIR')
            for data_path in data_paths:
                install_directory(tg, env, data_path, '', 'DEPLOY_DATADIR')
            if name not in build_context.env.THIRDPARTIES_FIRST:
                bin_paths = expand_nodepath(
                    build_context, [
                        i for i in [source_node.make_node('bin')] +
                                   [source_node.make_node('bin.%s' % platform)
                                    for platform in platform_specific] if os.path.isdir(i.abspath())
                    ]
                )
                data_paths = [
                    i for i in [source_node.make_node('data')] +
                               [source_node.make_node('data.%s' % platform) for platform in platform_specific]
                    if os.path.isdir(i.abspath())
                ]
                for bin_path in bin_paths:
                    install_directory(tg, env, bin_path, '', 'DEPLOY_RUNBINDIR')
                for data_path in data_paths:
                    install_directory(tg, env, data_path, '', 'DEPLOY_DATADIR')
                build_context.env.append_unique('THIRDPARTIES_FIRST', name)
            return tg
        else:
            return None
