import os
import waflib.TaskGen
import waflib.Tools.gcc
import waflib.Tools.ccroot
import waflib.Task
import waflib.Utils
import waflib.Node
import waflib.Context
from typing import Any, List, Optional, Union
from ..build import make_bld_node
from ..modules import external
from ..install import install_files, install_as
from ...options import BuildContext


def setup_build_macos(build_context: BuildContext) -> None:
    build_context.platforms.append(external(build_context, 'motor.3rdparty.system.cocoa'))

    def wrap_class(class_name: str) -> None:
        cls = waflib.Task.classes.get(class_name, None)
        assert cls is not None
        derived = type(class_name, (cls,), {})

        def exec_command_clean(self: waflib.Task.Task, cmd: Union[List[str], str], **kw: Any) -> int:
            self.outputs[0].delete(evict=False)
            return cls.exec_command(self, cmd, **kw)

        setattr(derived, 'exec_command', exec_command_clean)

    for cls_name in 'cshlib', 'cxxshlib', 'cprogram', 'cxxprogram', 'lipo':
        wrap_class(cls_name)


@waflib.TaskGen.extension('.plist')
def install_plist_darwin(self: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    if 'darwin' in self.bld.env.VALID_PLATFORMS:
        bld_env = self.bld.env
        if bld_env.SUB_TOOLCHAINS:
            bld_env = self.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
        install_files(self, os.path.join(self.bld.env.PREFIX, self.bld.env.OPTIM, bld_env.DEPLOY_ROOTDIR), [node])


@waflib.TaskGen.feature('cshlib', 'cxxshlib')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('process_use')
def set_darwin_shlib_name(self: waflib.TaskGen.task_gen) -> None:
    if 'darwin' in self.env.VALID_PLATFORMS:
        bin_path = os.path.join(self.env.PREFIX, self.env.DEPLOY_BINDIR)
        plugin_path = os.path.join(self.env.PREFIX, self.env.DEPLOY_PLUGINDIR)
        kernel_path = os.path.join(self.env.PREFIX, self.env.DEPLOY_KERNELDIR)
        link_task = getattr(self, 'link_task')  # type: waflib.Task.Task
        if 'motor:plugin' in self.features:
            rel_path = os.path.relpath(plugin_path, bin_path)
            self.env.append_unique(
                'LINKFLAGS', ['-install_name',
                              os.path.join('@executable_path', rel_path, link_task.outputs[0].name)]
            )
        elif 'motor:kernel' in self.features:
            rel_path = os.path.relpath(kernel_path, bin_path)
            self.env.append_unique(
                'LINKFLAGS', ['-install_name',
                              os.path.join('@executable_path', rel_path, link_task.outputs[0].name)]
            )
        else:
            self.env.append_unique(
                'LINKFLAGS',
                ['-install_name', os.path.join('@executable_path', link_task.outputs[0].name)]
            )


@waflib.TaskGen.feature('cprogram', 'cxxprogram', 'cshlib', 'cxxshlib')
@waflib.TaskGen.after_method('apply_link')
def add_objc_lib(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'darwin' in task_gen.env.VALID_PLATFORMS:
        task_gen.env.append_unique('LINKFLAGS', [
            '-l',
            'objc',
        ])


@waflib.TaskGen.feature('cprogram', 'cxxprogram')
@waflib.TaskGen.after_method('apply_link')
def set_osx_rpath(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'darwin' in task_gen.env.VALID_PLATFORMS:
        bin_path = os.path.join(task_gen.env.PREFIX, task_gen.env.DEPLOY_BINDIR)
        plugin_path = os.path.join(task_gen.env.PREFIX, task_gen.env.DEPLOY_PLUGINDIR)
        kernel_path = os.path.join(task_gen.env.PREFIX, task_gen.env.DEPLOY_KERNELDIR)
        rel_plugin_path = os.path.relpath(plugin_path, bin_path)
        task_gen.env.append_unique('RPATH', '@executable_path')
        task_gen.env.append_unique('RPATH', [os.path.join('@executable_path', rel_plugin_path)])
        rel_kernel_path = os.path.relpath(kernel_path, bin_path)
        if rel_kernel_path != rel_plugin_path:
            task_gen.env.append_unique('RPATH', [os.path.join('@executable_path', rel_kernel_path)])


dsym = '${DSYMUTIL} ${DSYMUTILFLAGS} ${SRC} -o ${TGT[0].parent.parent.abspath()}'
waflib.Task.task_factory('dsym', dsym, color='BLUE')
strip = '${STRIP} ${STRIPFLAGS} -S -x -o ${TGT[0].abspath()} ${SRC[0].abspath()}'
waflib.Task.task_factory('strip', strip, color='BLUE')
lipo = '${LIPO} ${LIPOFLAGS} ${SRC} -create -output ${TGT[0].abspath()}'
waflib.Task.task_factory('lipo', lipo, color='BLUE')


class codesign(waflib.Task.Task):

    def run(self) -> int:
        self.outputs[0].write(self.inputs[0].read('rb'), 'wb')
        return self.exec_command(self.env.CODESIGN + ['-s-', self.outputs[0].abspath()])


def _darwin_postlink_task(task_gen: waflib.TaskGen.task_gen, link_task: waflib.Task.Task) -> Optional[waflib.Task.Task]:
    if 'cxxtest' in task_gen.features:
        return None
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, task_gen.bld.srcnode.name)  # type: str

    bldnode = task_gen.bld.bldnode
    out_rootdir = os.path.join(appname + '.app.dSYM', 'Contents')
    out_rootnode = bldnode.make_node(out_rootdir)
    out_dsymdir = out_rootnode.make_node('Resources/DWARF')

    out_node = link_task.outputs[0]
    out_node_stripped = out_node.change_ext('.stripped')
    out_node_signed = make_bld_node(task_gen, 'bin.signed', None, out_node.name)
    strip_task = task_gen.create_task('strip', [out_node], [out_node_stripped])

    if task_gen.env.CODESIGN:
        sign_task = task_gen.create_task('codesign', [out_node_stripped], [out_node_signed])
        link_task = sign_task
    else:
        link_task = strip_task
    setattr(task_gen, 'link_task', link_task)

    if task_gen.env.DSYMUTIL:
        dsymtask = getattr(task_gen.bld, 'dsym_task', None)
        if not dsymtask:
            infoplist = out_rootnode.make_node('Info.plist')
            dsymtask = task_gen.create_task('dsym', [], [infoplist])
            setattr(task_gen.bld, 'dsym_task', dsymtask)
            install_as(
                task_gen, os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, infoplist.path_from(bldnode)),
                infoplist
            )

        dsymtask.set_inputs(out_node)
        dsymtask.set_outputs(out_dsymdir.make_node(out_node.name))
        install_as(
            task_gen,
            os.path.join(
                task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, appname + '.app.dSYM', 'Contents', 'Resources',
                'DWARF', out_node.name
            ), dsymtask.outputs[-1]
        )
    return link_task


@waflib.TaskGen.feature('cshlib', 'cxxshlib', 'cprogram', 'cxxprogram')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('process_use')
@waflib.TaskGen.before_method('install_step')
def apply_postlink_darwin(self: waflib.TaskGen.task_gen) -> None:
    if 'darwin' in self.env.VALID_PLATFORMS:
        if not self.env.SUBARCH:
            _darwin_postlink_task(self, getattr(self, 'link_task'))


@waflib.TaskGen.feature('motor:multiarch')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('process_use')
@waflib.TaskGen.after_method('apply_postlink_darwin')
@waflib.TaskGen.before_method('install_step')
def apply_multiarch_darwin(self: waflib.TaskGen.task_gen) -> None:
    if 'darwin' in self.env.VALID_PLATFORMS:
        features = []
        inputs = []
        task_gen = self
        for tg_name in getattr(self, 'use', []):
            task_gen = self.bld.get_tgen_by_name(tg_name)
            task_gen.post()
            if getattr(task_gen, 'link_task', None):
                inputs.append(getattr(task_gen, 'link_task').outputs[0])
                features += task_gen.features
        if 'motor:plugin' in features:
            out_name = task_gen.env.cxxshlib_PATTERN % self.target
            out_path = self.env.DEPLOY_PLUGINDIR
        elif 'motor:kernel' in features:
            out_name = task_gen.env.cxxshlib_PATTERN % self.target
            out_path = self.env.DEPLOY_KERNELDIR
        elif 'cshlib' in features or 'cxxshlib' in features:
            out_name = task_gen.env.cxxshlib_PATTERN % self.target
            out_path = self.env.DEPLOY_RUNBINDIR
        elif 'cprogram' in features or 'cxxprogram' in features:
            out_name = task_gen.env.cxxprogram_PATTERN % self.target
            out_path = self.env.DEPLOY_BINDIR
        else:
            return

        out_node_full = make_bld_node(self, 'bin', None, out_name)

        lipo_task = self.create_task('lipo', inputs, [out_node_full])
        link_task = _darwin_postlink_task(self, lipo_task)
        if link_task is not None:
            install_as(
                self,
                os.path.join(self.bld.env.PREFIX, self.bld.env.OPTIM, out_path, out_name),
                link_task.outputs[0],
                chmod=waflib.Utils.O755
            )
