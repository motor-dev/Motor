import os
import waflib.ConfigSet
import waflib.Configure
import waflib.Context
import waflib.Node
import waflib.Options
import waflib.Task
import waflib.TaskGen
import waflib.Utils
import build_framework
from typing import List, Optional


@waflib.Configure.conf
def python_module(
        build_context: waflib.Context.Context,
        name: str,
        depends: Optional[List[str]] = None,
        path: Optional[waflib.Node.Node] = None,
        uselib: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None
) -> Optional[waflib.TaskGen.task_gen]:
    assert isinstance(build_context, build_framework.BuildContext)

    def python_lib(env: waflib.ConfigSet.ConfigSet) -> Optional[waflib.TaskGen.task_gen]:
        features = (['c', 'cxx', 'cxxshlib', 'motor:c', 'motor:cxx', 'motor:shared_lib', 'motor:python_module'])
        result = build_framework.module(
            build_context,
            name,
            env,
            path,
            depends,
            [],
            features,
            None,
            [],
            [],
            [],
            [],
            [],
            conditions,
            None,
            uselib
        )
        if result is not None:
            result.env.cxxshlib_PATTERN = result.env.pymodule_PATTERN
        return result

    build_framework.preprocess(
        build_context,
        name,
        path,
        'Motor',
        name,
        depends=depends,
        uselib=uselib,
        conditions=conditions,
        extra_features=['motor:preprocess:python_module']
    )
    multiarch_module = build_framework.multiarch(
        build_context,
        name,
        [python_lib(env) for env in build_context.multiarch_envs]
    )
    if multiarch_module is not None:
        multiarch_module.env.cxxshlib_PATTERN = multiarch_module.env.pymodule_PATTERN
    return multiarch_module


@waflib.TaskGen.feature('motor:python_module')
@waflib.TaskGen.after_method('install_step')
def install_python_module(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.PROJECTS and not task_gen.env.ENV_PREFIX:  # no multiarch
        build_framework.install_files(
            task_gen,
            os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, task_gen.bld.env.DEPLOY_RUNBINDIR),
            [getattr(task_gen, 'postlink_task').outputs[0]], waflib.Utils.O755
        )
        if task_gen.env.CC_NAME == 'msvc':
            build_framework.install_files(
                task_gen,
                os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, task_gen.bld.env.DEPLOY_RUNBINDIR),
                [getattr(task_gen, 'link_task').outputs[1]]
            )


def build(build_context: build_framework.BuildContext) -> None:
    build_context.env.PYTHON_VERSIONS = waflib.Options.options.python_versions.split(',')
    for version in build_context.env.PYTHON_VERSIONS:
        build_context.recurse('tcltk/build.py')
        version_number = version.replace('.', '')
        for env in build_context.multiarch_envs:
            path = env['PYTHON%s_BINARY' % version_number]
            if path:
                path = build_context.package_node.make_node(path)
                build_framework.thirdparty(
                    build_context,
                    'motor.3rdparty.scripting.python%s' % version_number,
                    var='python%s' % version_number,
                    source_node=path,
                    private_use=['motor.3rdparty.scripting.tcltk'],
                    feature_list=['python', 'python' + version],
                    env=env
                )
                build_framework.add_feature(build_context, 'python', env)
            else:
                build_framework.thirdparty(
                    build_context,
                    'motor.3rdparty.scripting.python%s' % version_number,
                    var='python%s' % version_number,
                    private_use=['motor.3rdparty.scripting.tcltk'],
                    feature_list=['python', 'python' + version],
                    env=env
                )
