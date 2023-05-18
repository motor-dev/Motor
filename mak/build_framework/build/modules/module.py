import os
import re
from waflib import Errors, Options
from waflib.Configure import conf
from waflib.TaskGen import extension

COMPILE_EXTENSIONS = ['cxx', 'cpp', 'cc', 'c', 'rc', 'm', 'mm', 'def', 'masm']


def safe_name(name):
    name = name.replace('-', '_')
    name = name.replace('+', 'x')
    return name


@conf
def add_feature(self, feature, env=None):
    if env:
        env.append_unique('FEATURES', feature)
    else:
        for env in self.multiarch_envs:
            env.append_unique('FEATURES', feature)


def get_source_nodes(build_context, path, name):
    if path is None:
        path = build_context.path
        for n in name.split('.'):
            path = path.find_node(n)
            if not path:
                raise Errors.WafError('could not find module %s in %s' % (name, build_context.path.abspath()))
    source_nodes = [('', path)]
    if path.is_child_of(build_context.motornode):
        relative_path = path.path_from(build_context.motornode)
        for platform in build_context.motornode.find_node('extra').listdir():
            if build_context.env.PROJECTS or platform in build_context.env.VALID_PLATFORMS:
                node = build_context.motornode.find_node('extra').find_node(platform).find_node(relative_path)
                if node:
                    source_nodes.append(('[%s]' % platform, node))
    return source_nodes


@conf
def preprocess(build_context, name, path, root_namespace, plugin_name, depends, uselib, extra_features=[]):
    source_nodes = get_source_nodes(build_context, path, name)

    pp_env = build_context.common_env.derive()
    pp_env.PLUGIN = plugin_name.replace('.', '_')

    preprocess_sources = []
    if build_context.env.PROJECTS:
        globs = ['nothing']
    else:
        globs = ['src/**/*.yy', 'src/**/*.ll', 'src/**/*.plist', 'api/**/*.meta.hh', 'include/**/*.meta.hh']
    for _, source_node in source_nodes:
        preprocess_sources += source_node.ant_glob(globs, excl=[])

    use = []
    for d in depends:
        try:
            d = build_context.get_tgen_by_name(d + '.preprocess')
        except Errors.WafError:
            pass
        else:
            use.append(d.target)

    preprocess = build_context(
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
        generated_include_node=build_context.bldnode.make_node(name + '.preprocess/include'),
        use=use
    )

    for _, source_node in source_nodes:
        if os.path.isdir(os.path.join(source_node.abspath(), 'kernels')):
            kernelspath = source_node.make_node('kernels')
            for kernel in kernelspath.ant_glob('**', excl=[]):
                kernel_name, kernel_ext = os.path.splitext(kernel.path_from(kernelspath))
                kernel_name = re.split('[\\\\/]', kernel_name)
                preprocess.kernels.append((kernel_name, kernel))

    return preprocess


@conf
def module(
        build_context, name, env, path, depends, private_depends, features, source_list, extra_includes,
        extra_public_includes, extra_system_includes, extra_defines, extra_public_defines, conditions, project_name,
        uselib,
        **kw_args
):
    if not env.PROJECTS:
        for condition in conditions:
            if condition not in env.FEATURES:
                return None
    source_nodes = get_source_nodes(build_context, path, name)
    source_filter = ['src/**/*.%s' % ext for ext in COMPILE_EXTENSIONS]
    includes = []
    api = []
    platform_specific = ['']
    platform_specific += ['.%s' % p for p in env.VALID_PLATFORMS]
    platform_specific += ['.%s' % a for a in env.VALID_ARCHITECTURES]
    platform_specific += ['.%s.%s' % (p, a) for p in env.VALID_PLATFORMS for a in env.VALID_ARCHITECTURES]
    if source_list is None:
        source_list = []
        for _, node in source_nodes:
            source_list.append(node.ant_glob(source_filter))
            for suffix in platform_specific:
                if node.find_node('include%s' % suffix):
                    includes.append(node.find_node('include%s' % suffix))
                if node.find_node('api%s' % suffix):
                    api.append(node.find_node('api%s' % suffix))
    elif source_list:
        source_list = source_nodes[0][1].ant_glob(source_list)
    else:
        source_list = []
    preprocess = build_context.get_tgen_by_name('%s.preprocess' % name)
    extra_includes = extra_includes + [preprocess.generated_include_node]

    module_path = None
    if path:
        path_node = source_nodes[0][1]
        if path_node.is_child_of(build_context.path):
            module_path = path_node.path_from(build_context.path).replace('/', '.').replace('\\', '. ')
        elif path_node.is_child_of(build_context.package_node):
            pass
        elif path_node.is_child_of(build_context.motornode):
            module_path = path_node.path_from(build_context.motornode).replace('/', '.').replace('\\', '. ')

    task_gen = build_context(
        env=env.derive(),
        target=env.ENV_PREFIX % name,
        target_name=name,
        safe_target_name=safe_name(name.split('.')[-1]),
        features=features[:],
        use=[env.ENV_PREFIX % d for d in depends],
        private_use=[env.ENV_PREFIX % d for d in private_depends],
        uselib=[build_context.__class__.optim] + (build_context.env.STATIC and ['static'] or ['dynamic']) + uselib,
        preprocess=preprocess,
        source_nodes=source_nodes,
        source=source_list,
        defines=[
                    'building_%s' % safe_name(name.split('.')[-1]),
                    'MOTOR_PROJECTID=%s' % safe_name(name.replace('.', '_')),
                    'MOTOR_PROJECTNAME=%s' % name
                ] + extra_defines,
        export_defines=extra_public_defines[:],
        includes=extra_includes + includes + api + [build_context.srcnode],
        export_includes=extra_public_includes + api,
        export_system_includes=extra_system_includes,
        project_name=project_name or name,
        conditions=conditions,
    )
    if module_path is not None:
        task_gen.module_path = module_path

    if Options.options.tests and env.BUILD_UNIT_TESTS:
        for _, source_node in source_nodes:
            if os.path.isdir(os.path.join(source_node.abspath(), 'tests')):
                test_path = source_node.make_node('tests')
                for test in test_path.ant_glob('**', excl=[]):
                    test_name = os.path.splitext(test.path_from(test_path))[0]
                    test_name = re.split('[\\\\/]', test_name)
                    target_name = 'unittest.%s.%s' % (name, '.'.join(test_name))
                    p = build_context.preprocess(
                        target_name + '.preprocess',
                        test_path,
                        preprocess.root_namespace,
                        preprocess.plugin_name,
                        depends=[task_gen.target],
                        uselib=uselib,
                        extra_features=['motor:module']
                    )

                    build_context(
                        env=env.derive(),
                        preprocess=p,
                        target=env.ENV_PREFIX % target_name,
                        target_name=target_name,
                        safe_target_name=safe_name(test_name[-1]),
                        features=['cxx', 'cxxprogram', 'motor:cxx', 'motor:unit_test'],
                        use=[task_gen.target],
                        uselib=[build_context.__class__.optim] +
                               (build_context.env.STATIC and ['static'] or ['dynamic']) + uselib,
                        source=[test],
                        source_nodes=source_nodes,
                        defines=[
                            'building_%s' % safe_name(test_name[-1]),
                            'MOTOR_PROJECTID=%s' % safe_name('_'.join(test_name)),
                            'MOTOR_PROJECTNAME=%s' % target_name
                        ],
                        includes=extra_includes + includes + api + [p
                                                                    for _, p in source_nodes] + [build_context.srcnode],
                        conditions=conditions,
                    )

    return task_gen


@conf
def multiarch(build_context, name, arch_modules):
    arch_modules = [m for m in arch_modules if m is not None]
    if arch_modules:
        if len(build_context.multiarch_envs) == 1:
            task_gen = arch_modules[0]
        else:
            task_gen = build_context(
                target=name,
                features=['motor:multiarch'],
                use=[arch_module.target for arch_module in arch_modules],
            )
        return task_gen
    else:
        return None


@extension('.cl')
def handle_cl(self, cl_file):
    pass


def build(build_context):
    pass
