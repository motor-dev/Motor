import os
import build_framework
import waflib.Node
import waflib.Options
import waflib.Task
import waflib.TaskGen
import waflib.Utils
from typing import Optional


@waflib.TaskGen.feature('motor:android:aapt_resource')
def aapt_resource(task_gen: waflib.TaskGen.task_gen) -> None:
    destfile = getattr(task_gen, 'destfile')  # type: waflib.Node.Node
    resource = getattr(task_gen, 'resource')  # type: waflib.Node.Node
    manifest = build_framework.make_bld_node(task_gen, 'src', '', 'AndroidManifest.xml')
    task_gen.create_task('android_mft', [], manifest)
    tsk = task_gen.create_task('aapt_create', resource.ant_glob('**/*'), [destfile])
    tsk.env.MANIFEST = manifest.abspath()
    tsk.env.RESOURCE_PATH = resource.abspath()
    tsk.dep_nodes = [manifest]
    nodes = [resource]
    while nodes:
        node = nodes.pop()
        if os.path.isdir(node.abspath()):
            nodes.extend([node.make_node(i) for i in node.listdir()])
        else:
            tsk.dep_nodes.append(node)


@waflib.TaskGen.feature('javac')
@waflib.TaskGen.before_method('apply_java')
def set_dirs(task_gen: waflib.TaskGen.task_gen) -> None:
    basedir = build_framework.make_bld_node(task_gen, 'jar', '', '')
    setattr(task_gen, 'basedir', basedir)
    setattr(task_gen, 'outdir', basedir)


@waflib.TaskGen.feature('dex')
@waflib.TaskGen.after_method('apply_java')
@waflib.TaskGen.before_method('process_source')
def dex_files(task_gen: waflib.TaskGen.task_gen) -> None:
    """
    Create a dex task. There can be only one dex task by task generator.
    """
    basedir = getattr(task_gen, 'basedir')  # type: waflib.Node.Node
    outdir = getattr(task_gen, 'outdir')  # type: waflib.Node.Node
    outdir.mkdir()
    destfile = outdir.find_or_declare(getattr(task_gen, 'destfile'))

    if task_gen.env.D8:
        task_name = 'd8'
    else:
        task_name = 'dex'
    tsk = task_gen.create_task(task_name, [], [destfile], basedir=basedir, outdir=outdir, cwd=outdir.abspath())

    build_framework.install_files(task_gen, os.path.join(task_gen.bld.env.PREFIX, task_gen.bld.env.OPTIM), [destfile])

    javac_task = getattr(task_gen, 'javac_task', None)  # type: Optional[waflib.Task.Task]
    if javac_task is not None:
        tsk.set_run_after(javac_task)


@waflib.TaskGen.feature('motor:multiarch')
def apply_multiarch_android(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('cprogram', 'cxxprogram', 'cshlib', 'cxxshlib')
@waflib.TaskGen.before_method('install_step')
@waflib.TaskGen.after_method('set_postlink_task')
def strip_debug_info(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.env.ENV_PREFIX:
        build_framework.create_strip_task(task_gen)


@waflib.TaskGen.feature('motor:launcher')
@waflib.TaskGen.after_method('install_step')
def install_program_android(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'android' in task_gen.env.VALID_PLATFORMS:
        target_name = getattr(task_gen, 'target_name')  # type: str
        postlink_task = getattr(task_gen, 'postlink_task')  # type: waflib.Task.Task
        if task_gen.env.ENV_PREFIX:  # in multiarch, also install the lib
            build_framework.install_as(
                task_gen,
                os.path.join(
                    task_gen.env.PREFIX, task_gen.env.OPTIM, task_gen.env.DEPLOY_BINDIR,
                    task_gen.env.cxxprogram_PATTERN % target_name
                ),
                postlink_task.outputs[0],
                chmod=waflib.Utils.O755
            )


def build(build_context: build_framework.BuildContext) -> None:
    if waflib.Options.options.android_jdk:
        if not build_context.env.env:
            build_context.env.env = dict(os.environ)
        build_context.env.env['JAVA_HOME'] = waflib.Options.options.android_jdk
        build_context.env.env['JRE_HOME'] = os.path.join(waflib.Options.options.android_jdk, 'jre')

    build_context.recurse('install.py')
    build_context.recurse('tasks.py')
