import os
import build_framework
import waflib.TaskGen
import waflib.Node
import waflib.Task
import waflib.ConfigSet
from typing import Optional

FT_SOURCE_LIST = [
    'src/autofit/autofit.c',
    'src/base/ftbase.c',
    'src/base/ftbbox.c',
    'src/base/ftbdf.c',
    'src/base/ftbitmap.c',
    'src/base/ftcid.c',
    'src/base/ftdebug.c',
    'src/base/ftfstype.c',
    'src/base/ftgasp.c',
    'src/base/ftglyph.c',
    'src/base/ftgxval.c',
    'src/base/ftinit.c',
    'src/base/ftmm.c',
    'src/base/ftotval.c',
    'src/base/ftpatent.c',
    'src/base/ftpfr.c',
    'src/base/ftstroke.c',
    'src/base/ftsynth.c',
    'src/base/ftsystem.c',
    'src/base/fttype1.c',
    'src/base/ftwinfnt.c',
    'src/bdf/bdf.c',
    'src/bzip2/ftbzip2.c',
    # 'src/cache/ftcache.c',
    'src/cache/ftcbasic.c',
    'src/cache/ftccache.c',
    'src/cache/ftccmap.c',
    'src/cache/ftcglyph.c',
    'src/cache/ftcimage.c',
    'src/cache/ftcmanag.c',
    'src/cache/ftcmru.c',
    'src/cache/ftcsbits.c',
    'src/cff/cff.c',
    'src/cid/type1cid.c',
    'src/gxvalid/gxvalid.c',
    'src/gzip/ftgzip.c',
    'src/lzw/ftlzw.c',
    'src/otvalid/otvalid.c',
    'src/pcf/pcf.c',
    'src/pfr/pfr.c',
    'src/psaux/psaux.c',
    'src/pshinter/pshinter.c',
    'src/psnames/psnames.c',
    'src/raster/raster.c',
    'src/sfnt/sfnt.c',
    'src/smooth/smooth.c',
    'src/truetype/truetype.c',
    'src/type1/type1.c',
    'src/type42/type42.c',
    'src/winfonts/winfnt.c',
]


@waflib.TaskGen.feature('motor:deploy:freetype')
@waflib.TaskGen.after_method('install_step')
@waflib.TaskGen.after_method('apply_link')
def deploy_freetype_package(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if task_gen.env.PROJECTS:
        return

    path = getattr(task_gen, 'source_nodes')[0][1]
    ft_dest = 'freetype-2.10.2-%s-multiarch-%s' % (task_gen.env.VALID_PLATFORMS[0], task_gen.env.COMPILER_ABI)

    def deploy_to(node: waflib.Node.Node, subdir: str) -> None:
        if task_gen.bld.env.OPTIM == 'debug':
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', ft_dest, subdir, task_gen.bld.env.OPTIM, node.name),
                node,
                original_install=True
            )
        else:
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', ft_dest, subdir, node.name),
                node,
                original_install=True
            )

    if task_gen.env.TOOLCHAIN == task_gen.bld.multiarch_envs[0].TOOLCHAIN:
        include = path.make_node('include')
        for h in include.ant_glob(['**/*.*'], remove=False):
            build_framework.install_as(
                task_gen,
                os.path.join('bld', 'packages', ft_dest, 'api', h.path_from(include)),
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
    defines = ['FT2_BUILD_LIBRARY=1', 'FT_CONFIG_OPTION_SYSTEM_ZLIB=1', 'FT_CONFIG_OPTION_NO_ASSEMBLER']
    include_path = path.make_node('include')
    includes = []
    for i in include_path.listdir():
        includes.append(include_path.find_node(i))
    if build_context.env.STATIC:
        return build_framework.static_library(
            build_context,
            name, ['motor.3rdparty.system.zlib'],
            env=env,
            path=path,
            extra_includes=[include_path],
            extra_public_includes=[include_path],
            extra_defines=defines,
            features=[
                'motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off', 'motor:deploy:freetype'
            ],
            source_list=FT_SOURCE_LIST
        )
    else:
        if not build_context.env.DISABLE_DLLEXPORT:
            dll_flags = ['DLL_EXPORT']
            dll_features = []
        else:
            dll_flags = []
            dll_features = ['motor:export_all']
        return build_framework.shared_library(
            build_context,
            name, ['motor.3rdparty.system.zlib'],
            env=env,
            path=path,
            extra_includes=[include_path],
            extra_public_includes=[include_path],
            extra_defines=defines + dll_flags,
            features=[
                         'motor:masterfiles:off', 'motor:warnings:off', 'motor:deploy:off', 'motor:deploy:freetype'
                     ] + dll_features,
            source_list=FT_SOURCE_LIST
        )


def build_binary(
        build_context: build_framework.BuildContext,
        name: str,
        env: waflib.ConfigSet.ConfigSet,
        path: waflib.Node.Node
) -> Optional[waflib.TaskGen.task_gen]:
    return build_framework.thirdparty(build_context, name, source_node=path, use=['motor.3rdparty.system.zlib'],
                                      env=env)


def build(build_context: build_framework.BuildContext) -> None:
    build_framework.package(
        build_context,
        'motor.3rdparty.graphics.freetype',
        'FREETYPE_BINARY', build_binary,
        'FREETYPE_SOURCE', build_source
    )
