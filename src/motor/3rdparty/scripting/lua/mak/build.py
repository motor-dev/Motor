import os
import waflib.ConfigSet
import waflib.Node
import waflib.Task
import waflib.TaskGen
import build_framework
from typing import Optional

LUA_HEADERS = ['src/lauxlib.h', 'src/lua.h', 'src/luaconf.h', 'src/lualib.h']
LUA_SOURCES = [
    'src/lapi.c',
    'src/lcode.c',
    'src/lctype.c',
    'src/ldebug.c',
    'src/ldo.c',
    'src/ldump.c',
    'src/lfunc.c',
    'src/lgc.c',
    'src/llex.c',
    'src/lmem.c',
    'src/lobject.c',
    'src/lopcodes.c',
    'src/lparser.c',
    'src/lstate.c',
    'src/lstring.c',
    'src/ltable.c',
    'src/ltm.c',
    'src/lundump.c',
    'src/lvm.c',
    'src/lzio.c',
    'src/lauxlib.c',
    'src/lbaselib.c',
    'src/lbitlib.c',
    'src/lcorolib.c',
    'src/ldblib.c',
    'src/liolib.c',
    'src/lmathlib.c',
    # 'src/loslib.c',
    'src/lstrlib.c',
    'src/ltablib.c',
    'src/lutf8lib.c',
    'src/loadlib.c',
    # 'src/linit.c',
]


@waflib.TaskGen.feature('motor:deploy:lua')
@waflib.TaskGen.after_method('install_step')
@waflib.TaskGen.after_method('apply_link')
def deploy_lua_package(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if task_gen.env.PROJECTS:
        return
    path = getattr(task_gen, 'source_nodes')[0][1]
    lua_dest = 'lua-5.3.5-%s-multiarch-%s' % (task_gen.env.VALID_PLATFORMS[0], task_gen.env.COMPILER_ABI)
    src = path.make_node('src')

    def deploy_to(node: waflib.Node.Node, subdir: str) -> None:
        if task_gen.bld.env.OPTIM == 'debug':
            build_framework.install_as(
                task_gen,
                os.path.join('bld/packages', lua_dest, subdir, task_gen.bld.env.OPTIM, node.name),
                node,
                original_install=True
            )
        else:
            build_framework.install_as(
                task_gen,
                os.path.join('bld/packages', lua_dest, subdir, node.name),
                node,
                original_install=True
            )

    if task_gen.env.TOOLCHAIN == task_gen.bld.multiarch_envs[0].TOOLCHAIN:
        for h in path.ant_glob(LUA_HEADERS, remove=False):
            build_framework.install_as(
                task_gen,
                os.path.join('bld/packages', lua_dest, 'api', h.path_from(src)),
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
    if 'windows' in build_context.env.VALID_PLATFORMS and not build_context.env.DISABLE_DLLEXPORT:
        dll_flags = ['LUA_BUILD_AS_DLL']
        dll_features = []
    else:
        dll_flags = []
        dll_features = ['motor:export_all']
    extra_defines = ['LUA_LIB']
    if not build_context.env.PROJECTS:
        extra_defines.append('lua_getlocaledecpoint()=0x2e')
    if build_context.env.STATIC:
        return build_framework.static_library(
            build_context,
            name,
            env=env,
            path=path,
            extra_defines=extra_defines,
            extra_includes=[path.make_node('src')],
            extra_public_includes=[path.make_node('src')],
            features=['motor:masterfiles:off', 'motor:deploy:off', 'motor:deploy:lua', 'motor:warnings:off'],
            source_list=LUA_SOURCES
        )
    else:
        return build_framework.shared_library(
            build_context,
            name,
            env=env,
            path=path,
            extra_defines=extra_defines + dll_flags,
            extra_includes=[path.make_node('src')],
            extra_public_includes=[path.make_node('src')],
            features=dll_features + ['motor:masterfiles:off', 'motor:deploy:off', 'motor:deploy:lua',
                                     'motor:warnings:off'],
            source_list=LUA_SOURCES
        )


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(build_context, name, source_node=path, env=env,
                                      use=getattr(build_context, 'platforms'))


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(
        build_context,
        'motor.3rdparty.scripting.lua',
        'LUA_BINARY', build_binary,
        'LUA_SOURCE', build_source
    )
