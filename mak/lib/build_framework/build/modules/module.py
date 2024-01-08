import os
import re
import waflib.TaskGen
import waflib.Node
import waflib.ConfigSet
import waflib.Errors
import waflib.Options
from ...options import BuildContext
from ..features import create_compiled_task

from typing import Optional, List, Tuple, Union

COMPILE_EXTENSIONS = ['cxx', 'cpp', 'cc', 'c', 'rc', 'm', 'mm', 'def', 'masm']


def _safe_name(name: str) -> str:
    name = name.replace('-', '_')
    name = name.replace('+', 'x')
    return name


def _get_source_nodes(
        build_context: BuildContext,
        path: Optional[waflib.Node.Node],
        name: str
) -> List[Tuple[str, waflib.Node.Node]]:
    if path is None:
        path = build_context.path
        for n in name.split('.'):
            path = path.find_node(n)
            if not path:
                raise waflib.Errors.WafError('could not find module %s in %s' % (name, build_context.path.abspath()))
    source_nodes = [('', path)]
    if path.is_child_of(build_context.motornode):
        relative_path = path.path_from(build_context.motornode)
        for platform in build_context.motornode.make_node('extra').listdir():
            if build_context.env.PROJECTS or platform in build_context.env.VALID_PLATFORMS:
                node = build_context.motornode.make_node('extra').make_node(platform).find_node(relative_path)
                if node:
                    source_nodes.append(('[%s]' % platform, node))
    return source_nodes


def preprocess(
        build_context: BuildContext,
        name: str,
        path: Optional[waflib.Node.Node],
        root_namespace: str,
        plugin_name: str,
        depends: Optional[List[str]],
        uselib: Optional[List[str]],
        extra_features: Optional[List[str]]
) -> Optional[waflib.TaskGen.task_gen]:
    depends = depends or []
    uselib = uselib or []
    extra_features = extra_features or []
    source_nodes = _get_source_nodes(build_context, path, name)
    pp_env = build_context.common_env.derive()
    pp_env.PLUGIN = plugin_name.replace('.', '_')

    preprocess_sources = []
    globs = ['src/**/*.yy', 'src/**/*.ll', 'src/**/*.plist', 'api/**/*.meta.hh', 'include/**/*.meta.hh']
    for _, source_node in source_nodes:
        preprocess_sources += source_node.ant_glob(globs, excl=[], remove=False)

    use = []
    for d in depends:
        try:
            tgen = build_context.get_tgen_by_name(d + '.preprocess')
        except waflib.Errors.WafError:
            pass
        else:
            use.append(tgen.target)

    preprocess_tgen = build_context(
        group='preprocess',
        env=pp_env,
        target=name + '.preprocess',
        parent=name,
        features=['motor:preprocess'] + extra_features,
        source=preprocess_sources,
        kernels=[],
        kernels_cpu=[],
        plugin_name=plugin_name,
        source_nodes=source_nodes,
        root_namespace=root_namespace,
        uselib=uselib,
        out_sources=[],
        generated_include_node=build_context.bldnode.make_node('preprocess').make_node(name + '.preprocess/include'),
        generated_api_node=build_context.bldnode.make_node('preprocess').make_node(name + '.preprocess/api'),
        use=use,
        nomaster=set([])
    )

    for _, source_node in source_nodes:
        if os.path.isdir(os.path.join(source_node.abspath(), 'kernels')):
            kernelspath = source_node.make_node('kernels')
            for kernel in kernelspath.ant_glob('**', excl=[], remove=False):
                kernel_name, kernel_ext = os.path.splitext(kernel.path_from(kernelspath))
                kernel_name_list = re.split('[\\\\/]', kernel_name)
                getattr(preprocess_tgen, 'kernels').append((kernel_name_list, kernel))

    return preprocess_tgen


def module(
        build_context: BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: Optional[waflib.Node.Node],
        depends: Optional[List[str]],
        private_depends: Optional[List[str]],
        features: Optional[List[str]],
        source_list: Optional[List[str]],
        extra_includes: Optional[List[waflib.Node.Node]],
        extra_public_includes: Optional[List[waflib.Node.Node]],
        extra_system_includes: Optional[List[Union[waflib.Node.Node, str]]],
        extra_defines: Optional[List[str]],
        extra_public_defines: Optional[List[str]],
        conditions: Optional[List[str]],
        project_name: Optional[str],
        uselib: Optional[List[str]],
        root_namespace: str = ''
) -> Optional[waflib.TaskGen.task_gen]:
    depends = depends or []
    private_depends = private_depends or []
    features = features or []
    extra_includes = extra_includes or []
    extra_public_includes = extra_public_includes or []
    extra_system_includes = extra_system_includes or []
    extra_defines = extra_defines or []
    extra_public_defines = extra_public_defines or []
    conditions = conditions or []
    uselib = uselib or []
    do_build = True
    task_gen = None  # type: Optional[waflib.TaskGen.task_gen]
    project_name = project_name or name

    if not env.PROJECTS:
        for condition in conditions:
            if condition not in env.FEATURES:
                do_build = False

    source_nodes = _get_source_nodes(build_context, path, name)
    source_filter = ['src/**/*.%s' % ext for ext in COMPILE_EXTENSIONS]
    includes = []  # type: List[waflib.Node.Node]
    api = []  # type: List[waflib.Node.Node]
    platform_specific = ['']
    platform_specific += ['.%s' % p for p in env.VALID_PLATFORMS]
    platform_specific += ['.%s' % a for a in env.VALID_ARCHITECTURES]
    platform_specific += ['.%s.%s' % (p, a) for p in env.VALID_PLATFORMS for a in env.VALID_ARCHITECTURES]
    if source_list is None:
        source_files = []
        for _, node in source_nodes:
            source_files += node.ant_glob(source_filter, remove=False)
            for suffix in platform_specific:
                include_node = node.find_node('include%s' % suffix)
                if include_node is not None:
                    includes.append(include_node)
                include_node = node.find_node('api%s' % suffix)
                if include_node is not None:
                    api.append(include_node)
    elif source_list:
        source_files = source_nodes[0][1].ant_glob(source_list, remove=False)
    else:
        source_files = []
    preprocess_taskgen = build_context.get_tgen_by_name('%s.preprocess' % name)
    extra_includes = extra_includes + [getattr(preprocess_taskgen, 'generated_include_node')]
    extra_public_includes = extra_public_includes + [getattr(preprocess_taskgen, 'generated_api_node')]

    if do_build:
        task_gen = build_context(
            group=build_context.motor_variant,
            env=env.derive(),
            target=env.ENV_PREFIX % name,
            target_name=name,
            features=features[:],
            use=[env.ENV_PREFIX % d for d in depends],
            private_use=[env.ENV_PREFIX % d for d in private_depends],
            uselib=[build_context.__class__.optim] + (build_context.env.STATIC and ['static'] or ['dynamic']) + uselib,
            preprocess=preprocess_taskgen,
            source_nodes=source_nodes,
            source=source_files,
            defines=[
                        'building_%s' % _safe_name(name.split('.')[-1]),
                        'MOTOR_PROJECTID=%s' % _safe_name(name.replace('.', '_')),
                        'MOTOR_PROJECTNAME=%s' % name
                    ] + extra_defines,
            export_defines=extra_public_defines[:],
            includes=extra_includes + includes + api,
            export_includes=extra_public_includes + api,
            export_system_includes=extra_system_includes,
            project_name=project_name,
            conditions=conditions,
            nomaster=getattr(preprocess_taskgen, 'nomaster') if preprocess_taskgen is not None else set(),
        )

    for _, source_node in source_nodes:
        if os.path.isdir(os.path.join(source_node.abspath(), 'tests')):
            test_path = source_node.make_node('tests')
            for test in test_path.ant_glob('**', excl=[], remove=False):
                test_name = os.path.splitext(test.path_from(test_path))[0]
                test_name_list = re.split('[\\\\/]', test_name)
                target_name = 'unittest.%s.%s' % (name, '.'.join(test_name_list))
                try:
                    p = build_context.get_tgen_by_name(
                        target_name + '.preprocess')  # type: Optional[waflib.TaskGen.task_gen]
                except waflib.Errors.WafError:
                    p = preprocess(
                        build_context,
                        target_name,
                        test_path,
                        getattr(preprocess_taskgen, 'root_namespace'),
                        getattr(preprocess_taskgen, 'plugin_name'),
                        depends=[name],
                        uselib=uselib,
                        extra_features=['motor:module']
                    )

                if do_build and waflib.Options.options.tests and (env.BUILD_UNIT_TESTS or env.PROJECTS):
                    assert task_gen is not None
                    build_context(
                        group=build_context.motor_variant,
                        env=env.derive(),
                        preprocess=p,
                        target=env.ENV_PREFIX % target_name,
                        target_name=target_name,
                        features=['cxx', 'cxxprogram', 'motor:cxx', 'motor:unit_test'],
                        use=[task_gen.target],
                        uselib=([build_context.__class__.optim] +
                                (build_context.env.STATIC and ['static'] or ['dynamic']) + uselib),
                        source=[test],
                        source_nodes=[('', test)],
                        defines=[
                            'building_%s' % _safe_name(test_name_list[-1]),
                            'MOTOR_PROJECTID=%s' % _safe_name('_'.join(test_name_list)),
                            'MOTOR_PROJECTNAME=%s' % target_name
                        ],
                        includes=extra_includes + includes + api + [p
                                                                    for _, p in source_nodes],
                        conditions=conditions,
                        nomaster=getattr(p, 'nomaster'),
                        project_name=project_name + '.unittest.' + '.'.join(test_name_list)
                    )

    return task_gen


def multiarch(
        build_context: BuildContext,
        name: str,
        arch_modules: List[Optional[waflib.TaskGen.task_gen]]
) -> Optional[waflib.TaskGen.task_gen]:
    modules = [m for m in arch_modules if m is not None]
    if modules:
        if len(build_context.multiarch_envs) == 1:
            task_gen = modules[0]
        else:
            task_gen = build_context(
                group=build_context.motor_variant,
                target=name,
                features=['motor:multiarch'],
                use=[arch_module.target for arch_module in modules],
            )
        return task_gen
    else:
        return None


@waflib.TaskGen.extension('.cl')
def handle_cl(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    if task_gen.env.PROJECTS:
        create_compiled_task(task_gen, 'cxx', node)
