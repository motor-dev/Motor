import os
import waflib.Task
import waflib.TaskGen
from .install import install_files
from typing import Any, List, Union


def _exec_command_objcopy(self: waflib.Task.Task, cmd: Union[List[str], str], **kw: Any) -> int:
    if isinstance(cmd, list):
        lst = []
        carry = ''
        for a in cmd:
            if a[-1] == '=':
                carry = a
            else:
                lst.append(carry + a)
                carry = ''
        cmd = lst
    return self.generator.bld.exec_command(cmd, **kw)


waflib.Task.task_factory('dbg_copy', '${OBJCOPY} --only-keep-debug ${SRC} ${TGT[0].abspath()}', color='YELLOW')
dbg_strip_cls = waflib.Task.task_factory(
    'dbg_strip',
    '${OBJCOPY} --strip-all --add-gnu-debuglink=${SRC[0].name} ${SRC[1].abspath()} ${TGT[0].abspath()}',
    color='YELLOW'
)
setattr(dbg_strip_cls, 'exec_command', _exec_command_objcopy)


def create_strip_task(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.env.STRIP_BINARY and task_gen.env.STRIP and task_gen.env.OBJCOPY and False:
        if task_gen.bld.env.OPTIM:
            task_gen.full_link_task = getattr(task_gen, 'link_task')
            full_link = task_gen.full_link_task.outputs[0]
            out_dir = full_link.parent.make_node('post-link')
            out_dir.mkdir()
            debug_prog = out_dir.make_node(full_link.name + '.debug')
            stripped_linked_prog = out_dir.make_node(full_link.name)

            task_gen.dbg_copy_task = task_gen.create_task('dbg_copy', [full_link], [debug_prog])
            task_gen.dbg_strip_task = task_gen.create_task('dbg_strip', [debug_prog, full_link], [stripped_linked_prog])
            task_gen.dbg_strip_task.cwd = out_dir.abspath()
            task_gen.postlink_task = task_gen.dbg_strip_task

            if 'motor:plugin' in task_gen.features:
                out_path = task_gen.env.DEPLOY_PLUGINDIR
            elif 'motor:kernel' in task_gen.features:
                out_path = task_gen.env.DEPLOY_KERNELDIR
            elif 'motor:shared_lib' in task_gen.features:
                out_path = task_gen.env.DEPLOY_RUNBINDIR
            elif 'motor:launcher' in task_gen.features:
                out_path = task_gen.env.DEPLOY_BINDIR
            else:
                return

            install_files(task_gen, os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, out_path),
                          [debug_prog])


@waflib.TaskGen.feature('cprogram', 'cxxprogram', 'cshlib', 'cxxshlib')
@waflib.TaskGen.before_method('install_step')
@waflib.TaskGen.after_method('set_postlink_task')
def strip_debug_info(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.SUBARCH:
        create_strip_task(task_gen)
