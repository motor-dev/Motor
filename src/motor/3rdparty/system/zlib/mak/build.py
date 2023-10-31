import os
import waflib.ConfigSet
import waflib.Node
import waflib.Task
import waflib.TaskGen
import build_framework
from typing import Optional

ZLIB_SOURCE_LIST = [
    'adler32.c',
    'compress.c',
    'crc32.c',
    'deflate.c',
    'gzclose.c',
    'gzlib.c',
    'gzread.c',
    'gzwrite.c',
    'infback.c',
    'inffast.c',
    'inflate.c',
    'inftrees.c',
    'trees.c',
    'uncompr.c',
    'zutil.c',
]
MINIZIP_SOURCE_LIST = ['contrib/minizip/ioapi.c', 'contrib/minizip/unzip.c']


@waflib.TaskGen.feature('motor:deploy:zlib')
@waflib.TaskGen.after_method('install_step')
@waflib.TaskGen.after_method('apply_link')
def deploy_zlib_package(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if task_gen.env.PROJECTS:
        return

    path = getattr(task_gen, 'source_nodes')[0][1]
    zlib_dest = 'zlib-1.2.11-%s-multiarch-%s' % (task_gen.env.VALID_PLATFORMS[0], task_gen.env.COMPILER_ABI)

    def deploy_to(node: waflib.Node.Node, subdir: str) -> None:
        if task_gen.bld.env.OPTIM == 'debug':
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', zlib_dest, subdir, task_gen.bld.env.OPTIM, node.name),
                node,
                original_install=True
            )
        else:
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', zlib_dest, subdir, node.name),
                node,
                original_install=True
            )

    if task_gen.env.TOOLCHAIN == task_gen.bld.multiarch_envs[0].TOOLCHAIN:
        build_framework.install_as(
            task_gen,
            os.path.join('bld', 'packages', zlib_dest, 'api', 'zconf.h'),
            path.find_node('zconf.h'),
            original_install=True
        )
        build_framework.install_as(
            task_gen,
            os.path.join('bld', 'packages', zlib_dest, 'api', 'zlib.h'),
            path.find_node('zlib.h'),
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


@waflib.TaskGen.feature('motor:deploy:minizip')
@waflib.TaskGen.after_method('install_step')
@waflib.TaskGen.after_method('apply_link')
def deploy_minizip_package(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if task_gen.env.PROJECTS:
        return

    path = getattr(task_gen, 'source_nodes')[0][1]
    minizip_dest = 'minizip-1.2.11-%s-multiarch-%s' % (task_gen.env.VALID_PLATFORMS[0], task_gen.env.COMPILER_ABI)

    def deploy_to(node: waflib.Node.Node, subdir: str) -> None:
        if task_gen.bld.env.OPTIM == 'debug':
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', minizip_dest, subdir, task_gen.bld.env.OPTIM, node.name),
                node,
                original_install=True
            )
        else:
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', minizip_dest, subdir, node.name),
                node,
                original_install=True
            )

    if task_gen.env.TOOLCHAIN == task_gen.bld.multiarch_envs[0].TOOLCHAIN:
        build_framework.install_as(
            task_gen,
            os.path.join('bld', 'packages', minizip_dest, 'api', 'ioapi.h'),
            path.find_node('contrib/minizip/ioapi.h'),
            original_install=True
        )
        build_framework.install_as(
            task_gen,
            os.path.join('bld', 'packages', minizip_dest, 'api', 'unzip.h'),
            path.find_node('contrib/minizip/unzip.h'),
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


def build_zlib_source(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    if build_context.env.STATIC:
        return build_framework.static_library(
            build_context,
            name,
            ['motor.3rdparty.system.win32'],
            env=env,
            path=path,
            extra_includes=[path],
            extra_public_includes=[path],
            features=['motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off', 'motor:deploy:zlib'],
            source_list=ZLIB_SOURCE_LIST
        )
    else:
        if 'windows' in build_context.env.VALID_PLATFORMS and not build_context.env.DISABLE_DLLEXPORT:
            dll_flags = ['ZLIB_DLL']
            dll_features = []
        else:
            dll_flags = []
            dll_features = ['motor:export_all']
        return build_framework.shared_library(
            build_context,
            name, ['motor.3rdparty.system.win32'],
            env=env,
            path=path,
            extra_includes=[path],
            extra_public_includes=[path],
            extra_defines=['Z_HAVE_UNISTD_H'] + dll_flags,
            extra_public_defines=dll_flags,
            features=dll_features + ['motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off',
                                     'motor:deploy:zlib'],
            source_list=ZLIB_SOURCE_LIST
        )


def build_zlib_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    result = build_framework.thirdparty(build_context, name, source_node=path, env=env)
    assert result is not None
    if not build_context.env.STATIC:
        if 'windows' in build_context.env.VALID_PLATFORMS and not build_context.env.DISABLE_DLLEXPORT:
            getattr(result, 'export_defines').append('ZLIB_DLL')
    return result


def build_minizip_source(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    include_path = path.make_node('contrib/minizip')
    if build_context.env.STATIC:
        return build_framework.static_library(
            build_context,
            name,
            ['motor.3rdparty.system.zlib', 'motor.3rdparty.system.win32'],
            env=env,
            path=path,
            extra_includes=[include_path],
            extra_public_includes=[include_path],
            extra_defines=['USE_FILE32API', 'ZLIB_INTERNAL'],
            features=['motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off', 'motor:deploy:minizip'],
            source_list=MINIZIP_SOURCE_LIST
        )
    else:
        if 'windows' not in build_context.env.VALID_PLATFORMS:
            features = ['motor:export_all']
        else:
            features = []
        return build_framework.shared_library(
            build_context,
            name,
            ['motor.3rdparty.system.zlib', 'motor.3rdparty.system.win32'],
            env=env,
            path=path,
            extra_includes=[include_path],
            extra_public_includes=[include_path],
            extra_defines=['USE_FILE32API', 'ZLIB_INTERNAL'],
            features=features + ['motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off',
                                 'motor:deploy:minizip'],
            source_list=MINIZIP_SOURCE_LIST
        )


def build_minizip_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(
        build_context,
        name,
        var='minizip',
        source_node=path,
        use=['motor.3rdparty.system.zlib'],
        env=env
    )


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(
        build_context,
        'motor.3rdparty.system.zlib',
        'ZLIB_BINARY', build_zlib_binary,
        'ZLIB_SOURCE', build_zlib_source
    )
    build_framework.package(
        build_context,
        'motor.3rdparty.system.minizip',
        'MINIZIP_BINARY', build_minizip_binary,
        'MINIZIP_SOURCE', build_minizip_source
    )
