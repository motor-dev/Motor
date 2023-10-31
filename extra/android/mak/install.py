import os
import build_framework
import waflib.Errors
import waflib.Node
import waflib.TaskGen
import waflib.Utils
from typing import List


def install_files(
        task_gen: waflib.TaskGen.task_gen,
        out_dir: str,
        file_list: List[waflib.Node.Node],
        _: int = waflib.Utils.O644,
        __: bool = False
) -> None:
    assert 'android' in task_gen.env.VALID_PLATFORMS
    package_task = getattr(task_gen.bld, 'android_package_task')
    root_path = os.path.join(task_gen.env.PREFIX, task_gen.env.OPTIM)
    out_dir = out_dir[len(root_path) + 1:]
    for file in file_list:
        filename = file.path_from(task_gen.bld.bldnode)
        base = os.path.dirname(filename)
        if base != out_dir:
            dest_node = task_gen.bld.bldnode
            # dest_node = dest_node.make_node(self.bld.motor_variant)
            # dest_node = dest_node.make_node(self.bld.optim)
            dest_node = dest_node.make_node('zip')
            dest_node = dest_node.make_node(out_dir)
            dest_node.mkdir()
            dest_node = dest_node.find_or_declare(file.name)
            package_task.generator.create_task('copy', [file], [dest_node])
        else:
            dest_node = file
        package_task.set_inputs([dest_node])


def install_as(
        task_gen: waflib.TaskGen.task_gen,
        target_path: str,
        file: waflib.Node.Node,
        _: int = waflib.Utils.O644,
        __: bool = False
) -> None:
    assert 'android' in task_gen.env.VALID_PLATFORMS
    package_task = getattr(task_gen.bld, 'android_package_task')
    root_path = os.path.join(task_gen.env.PREFIX, task_gen.env.OPTIM)
    if not target_path.startswith(root_path):
        raise waflib.Errors.WafError('Does not know how to deploy to %s' % target_path)
    dest_node = task_gen.bld.bldnode
    # dest_node = dest_node.make_node(self.bld.motor_variant)
    # dest_node = dest_node.make_node(self.bld.optim)
    dest_node = dest_node.make_node('zip')
    dest_node = dest_node.find_or_declare(target_path[len(root_path) + 1:])
    package_task.generator.create_task('copy', [file], [dest_node])
    package_task.set_inputs([dest_node])


def build(build_context: build_framework.BuildContext) -> None:
    setattr(build_context, 'motor_install_files', install_files)
    setattr(build_context, 'motor_install_as', install_as)
