import os
import shutil
import waflib.Task
import waflib.Errors
import waflib.Utils
import waflib.Logs
import waflib.TaskGen
import waflib.ConfigSet
import waflib.Node

from typing import List


def install_files(
        task_gen: waflib.TaskGen.task_gen,
        out_dir: str,
        file_list: List[waflib.Node.Node],
        chmod: int = waflib.Utils.O644,
        original_install: bool = False
) -> None:
    if not original_install and hasattr(task_gen.bld, 'motor_install_files'):
        getattr(task_gen.bld, 'motor_install_files')(task_gen, out_dir, file_list, chmod, False)
        return
    try:
        install_task = getattr(task_gen, 'motor_install_task')
    except AttributeError:
        install_task = task_gen.create_task('install', [], [])
        setattr(task_gen, 'motor_install_task', install_task)
        install_task.install_step = []
    install_task.inputs += file_list
    for f in file_list:
        install_task.install_step.append((f, os.path.join(out_dir, f.name), chmod))


def install_as(
        task_gen: waflib.TaskGen.task_gen,
        target_path: str,
        file: waflib.Node.Node,
        chmod: int = waflib.Utils.O644,
        original_install: bool = False
) -> None:
    if not original_install and hasattr(task_gen.bld, 'motor_install_as'):
        getattr(task_gen.bld, 'motor_install_as')(task_gen, target_path, file, chmod, False)
        return
    try:
        install_task = getattr(task_gen, 'motor_install_task')
    except AttributeError:
        install_task = task_gen.create_task('install', [], [])
        setattr(task_gen, 'motor_install_task', install_task)
        install_task.install_step = []
    install_task.inputs.append(file)
    install_task.install_step.append((file, target_path, chmod))


def install_directory(
        task_gen: waflib.TaskGen.task_gen,
        env: waflib.ConfigSet.ConfigSet,
        node: waflib.Node.Node,
        local_path: str,
        env_variable: str,
        original_install: bool = False
) -> None:
    target_path = os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM, env[env_variable], local_path)
    for n in node.listdir():
        sn = node.make_node(n)
        if os.path.isdir(sn.abspath()):
            install_directory(task_gen, env, sn, os.path.join(local_path, n), env_variable, original_install)
        else:
            install_files(task_gen, target_path, [sn], original_install=original_install)


class install(waflib.Task.Task):
    color = 'CYAN'

    def runnable_status(self) -> int:
        ret = super(install, self).runnable_status()
        if ret != waflib.Task.ASK_LATER:
            for source, target, chmod in getattr(self, 'install_step'):
                d, _ = os.path.split(target)
                if not d:
                    raise waflib.Errors.WafError('Invalid installation given %r->%r' % (source, target))

                try:
                    st1 = os.stat(target)
                    st2 = os.stat(source.abspath())
                except OSError:
                    ret = waflib.Task.RUN_ME
                    break
                else:
                    # same size and identical timestamps -> make no copy
                    if st1.st_mtime + 2 < st2.st_mtime or st1.st_size != st2.st_size:
                        ret = waflib.Task.RUN_ME
                        break
        return ret

    def run(self) -> int:
        for source, target, chmod in getattr(self, 'install_step'):
            d, _ = os.path.split(target)
            waflib.Utils.check_dir(d)
            # following is for shared libs and stale inodes (-_-)
            try:
                os.remove(target)
            except OSError:
                pass

            try:
                shutil.copy2(source.abspath(), target)
                os.chmod(target, chmod)
            except IOError:
                try:
                    os.stat(source.abspath())
                except (OSError, IOError):
                    waflib.Logs.error('File %r does not exist' % source.abspath())
                    return 1
                waflib.Logs.error('Could not install the file %r' % target)
                return 1
        return 0


@waflib.TaskGen.feature('motor:deploy:off')
def dummy_features(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('motor:preprocess')
def install_module_files(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'motor:deploy:off' not in task_gen.features and not task_gen.env.PROJECTS:
        env = task_gen.env
        for _, source_node in getattr(task_gen, 'source_nodes', []):
            bin_paths = [
                i for i in [source_node.make_node('bin')] +
                           [source_node.make_node('bin.%s' % p) for p in env.VALID_PLATFORMS] if
                os.path.isdir(i.abspath())
            ]
            data_paths = [
                i for i in [source_node.make_node('data')] +
                           [source_node.make_node('data.%s' % p) for p in env.VALID_PLATFORMS] if
                os.path.isdir(i.abspath())
            ]
            for bin_path in bin_paths:
                install_directory(task_gen, env, bin_path, '', 'DEPLOY_RUNBINDIR')
            for data_path in data_paths:
                install_directory(task_gen, env, data_path, '', 'DEPLOY_DATADIR')


@waflib.TaskGen.feature('motor:kernel')
@waflib.TaskGen.after_method('install_step')
def install_kernel(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.SUBARCH and not task_gen.bld.env.STATIC:  # no multiarch, no static
        link_task = getattr(task_gen, 'link_task')
        postlink_task = getattr(task_gen, 'postlink_task')
        install_files(
            task_gen,
            os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'], task_gen.bld.env['DEPLOY_KERNELDIR']),
            [postlink_task.outputs[0]], waflib.Utils.O755
        )
        if task_gen.env.CC_NAME == 'msvc':
            install_files(task_gen,
                          os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'],
                                       task_gen.bld.env['DEPLOY_KERNELDIR']),
                          [link_task.outputs[1]]
                          )


@waflib.TaskGen.feature('motor:plugin')
@waflib.TaskGen.after_method('install_step')
def install_plugin(task_gen: waflib.TaskGen.task_gen) -> None:
    if ('cshlib' in task_gen.features) or ('cxxshlib' in task_gen.features):
        link_task = getattr(task_gen, 'link_task')
        postlink_task = getattr(task_gen, 'postlink_task')
        if not task_gen.env.SUBARCH:  # no multiarch
            install_files(
                task_gen,
                os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'],
                             task_gen.bld.env['DEPLOY_PLUGINDIR']),
                [postlink_task.outputs[0]], waflib.Utils.O755
            )
            if task_gen.env.CC_NAME == 'msvc':
                install_files(
                    task_gen,
                    os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'],
                                 task_gen.bld.env['DEPLOY_PLUGINDIR']),
                    [link_task.outputs[1]]
                )


@waflib.TaskGen.feature('motor:shared_lib')
@waflib.TaskGen.after_method('install_step')
def install_shared_lib(task_gen: waflib.TaskGen.task_gen) -> None:
    if ('cshlib' in task_gen.features) or ('cxxshlib' in task_gen.features):
        link_task = getattr(task_gen, 'link_task')
        postlink_task = getattr(task_gen, 'postlink_task')
        if not task_gen.env.SUBARCH:  # no multiarch
            install_files(
                task_gen,
                os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'],
                             task_gen.bld.env['DEPLOY_RUNBINDIR']),
                [postlink_task.outputs[0]], waflib.Utils.O755
            )
            if task_gen.env.CC_NAME == 'msvc':
                install_files(
                    task_gen,
                    os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'],
                                 task_gen.bld.env['DEPLOY_RUNBINDIR']),
                    [link_task.outputs[1]]
                )


@waflib.TaskGen.feature('motor:launcher')
@waflib.TaskGen.after_method('install_step')
def install_program(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.SUBARCH:  # no multiarch
        link_task = getattr(task_gen, 'link_task')
        postlink_task = getattr(task_gen, 'postlink_task')
        install_files(
            task_gen,
            os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'], task_gen.bld.env['DEPLOY_BINDIR']),
            [postlink_task.outputs[0]],
            chmod=waflib.Utils.O755
        )
        if task_gen.env.CC_NAME == 'msvc':
            install_files(
                task_gen,
                os.path.join(task_gen.bld.env['PREFIX'], task_gen.bld.env['OPTIM'], task_gen.bld.env['DEPLOY_BINDIR']),
                [link_task.outputs[1]]
            )


@waflib.TaskGen.feature('motor:game')
@waflib.TaskGen.after_method('install_step')
def install_game(_: waflib.TaskGen.task_gen) -> None:
    pass  # also plugin
