import os
import waflib.ConfigSet
import waflib.Node
import waflib.Task
import waflib.TaskGen
import build_framework
from typing import Optional


@waflib.TaskGen.feature('motor:deploy:bullet')
@waflib.TaskGen.after_method('install_step')
@waflib.TaskGen.after_method('apply_link')
def deploy_bullet_package(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if task_gen.env.PROJECTS:
        return

    path = getattr(task_gen, 'source_nodes')[0][1]
    bullet_dest = 'bullet-2.87-%s-multiarch-%s' % (task_gen.env.VALID_PLATFORMS[0], task_gen.env.COMPILER_ABI)
    src = path.make_node('src')

    def deploy_to(node: waflib.Node.Node, subdir: str) -> None:
        if task_gen.bld.env.OPTIM == 'debug':
            build_framework.install_as(
                task_gen,
                os.path.join('bld/packages', bullet_dest, subdir, task_gen.bld.env.OPTIM, node.name),
                node,
                original_install=True
            )
        else:
            build_framework.install_as(
                task_gen,
                os.path.join('bld/packages', bullet_dest, subdir, node.name),
                node,
                original_install=True
            )

    if task_gen.env.TOOLCHAIN == task_gen.bld.multiarch_envs[0].TOOLCHAIN:
        for h in src.ant_glob(
                ['*.h', 'BulletCollision/**/*.h', 'BulletDynamics/**/*.h', 'BulletSoftBody/**/*.h',
                 'LinearMath/**/*.h'], remove=False
        ):
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', bullet_dest, 'api', h.path_from(src)),
                h,
                original_install=True
            )
    link_task = getattr(task_gen, 'link_task')  # type: waflib.Task.Task
    if task_gen.env.STATIC:
        deploy_to(link_task.outputs[0], 'lib.%s' % task_gen.env.VALID_ARCHITECTURES[0])
    else:
        if task_gen.env.DEST_BINFMT == 'pe':
            for file in link_task.outputs[:-1]:
                deploy_to(file, 'bin.%s' % task_gen.env.VALID_ARCHITECTURES[0])
            deploy_to(link_task.outputs[-1], 'lib.%s' % task_gen.env.VALID_ARCHITECTURES[0])
        else:
            for file in link_task.outputs:
                deploy_to(file, 'bin.%s' % task_gen.env.VALID_ARCHITECTURES[0])


def build_source(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    if build_context.env.PROJECTS:
        return build_framework.headers(
            build_context,
            name,
            getattr(build_context, 'platforms'),
            path=path.make_node('src'),
            features=['motor:warnings:off', 'motor:deploy:off', 'motor:deploy:bullet'],
            extra_includes=[path.make_node('src')],
            extra_public_includes=[path.make_node('src')],
            extra_defines=[
                '_ALLOW_MSC_VER_MISMATCH=1', '_ALLOW_ITERATOR_DEBUG_LEVEL_MISMATCH=1',
                '_ALLOW_RUNTIME_LIBRARY_MISMATCH=1', 'BT_NO_PROFILE'
            ],
            env=env,
            source_list=[
                'BulletCollision/**/*.cpp', 'BulletDynamics/**/*.cpp', 'BulletSoftBody/**/*.cpp',
                'LinearMath/**/*.cpp'
            ],
            uselib=['cxx98']
        )
    elif build_context.env.STATIC:
        return build_framework.static_library(
            build_context,
            name,
            getattr(build_context, 'platforms'),
            path=path,
            features=['motor:warnings:off', 'motor:deploy:off', 'motor:deploy:bullet'],
            extra_includes=[path.make_node('src')],
            extra_system_includes=[path.make_node('src')],
            extra_defines=[
                '_ALLOW_MSC_VER_MISMATCH=1', '_ALLOW_ITERATOR_DEBUG_LEVEL_MISMATCH=1',
                '_ALLOW_RUNTIME_LIBRARY_MISMATCH=1', 'BT_NO_PROFILE'
            ],
            env=env,
            source_list=[
                'src/BulletCollision/**/*.cpp', 'src/BulletDynamics/**/*.cpp', 'src/BulletSoftBody/**/*.cpp',
                'src/LinearMath/**/*.cpp'
            ],
            uselib=['cxx98']
        )
    else:
        return build_framework.shared_library(
            build_context,
            name,
            getattr(build_context, 'platforms'),
            path=path,
            features=['motor:warnings:off', 'motor:deploy:off', 'motor:deploy:bullet', 'motor:export_all'],
            extra_includes=[path.make_node('src')],
            extra_system_includes=[path.make_node('src')],
            extra_defines=[
                '_ALLOW_MSC_VER_MISMATCH=1', '_ALLOW_ITERATOR_DEBUG_LEVEL_MISMATCH=1',
                '_ALLOW_RUNTIME_LIBRARY_MISMATCH=1', 'BT_NO_PROFILE'
            ],
            env=env,
            source_list=[
                'src/BulletCollision/**/*.cpp', 'src/BulletDynamics/**/*.cpp', 'src/BulletSoftBody/**/*.cpp',
                'src/LinearMath/**/*.cpp'
            ],
            uselib=['cxx98']
        )


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(
        build_context,
        name,
        source_node=path,
        env=env,
        use=getattr(build_context, 'platforms')
    )


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(
        build_context, 'motor.3rdparty.physics.bullet',
        'BULLET_BINARY', build_binary,
        'BULLET_SOURCE', build_source
    )
