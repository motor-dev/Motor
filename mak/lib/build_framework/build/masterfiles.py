import waflib.Build
import waflib.Errors
import waflib.Logs
import waflib.Node
import waflib.Options
import waflib.Task
import waflib.TaskGen
import waflib.Utils
import waflib.Tools.ccroot
from .features import create_compiled_task, make_bld_node


@waflib.TaskGen.feature('motor:masterfiles:off')
def masterfiles_feature(_: waflib.TaskGen.task_gen) -> None:
    pass


def _create_master_file(task: waflib.Task.Task) -> None:
    with open(task.outputs[0].abspath(), 'w') as f:
        for src in task.inputs:
            f.write('#include "%s"\n' % src.path_from(task.generator.bld.srcnode).replace('\\', '/'))


def _master_sig_deps(task: waflib.Task.Task) -> None:
    for f in sorted([i.srcpath().encode('utf8') for i in task.inputs]):
        task.m.update(f)
        task.m.update(b';')


MasterTask = waflib.Task.task_factory("master", _create_master_file, color='CYAN')
setattr(MasterTask, 'sig_explicit_deps', _master_sig_deps)


@waflib.TaskGen.extension('.c', '.m')
def c_hook(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    extension = getattr(task_gen, 'objc', False) and 'm' or 'c'
    if 'motor:c' in task_gen.features:
        category = getattr(task_gen, 'masterfiles').get(node, '')
        if category and not waflib.Options.options.nomaster and not task_gen.env.PROJECTS:
            try:
                mastertask_c = getattr(task_gen, 'mastertasks_c_%s' % category)
            except AttributeError:
                output = make_bld_node(
                    task_gen,
                    'src',
                    None,
                    'master-c-%s.%s' % (category, extension)
                )
                mastertask_c = task_gen.create_task('master', [node], [output])
                setattr(task_gen, 'mastertasks_c_%s' % category, mastertask_c)
                create_compiled_task(task_gen, 'c', output)
            else:
                mastertask_c.set_inputs([node])
        elif (
                category is not None
                and 'motor:masterfiles:off' not in task_gen.features
                and not waflib.Options.options.nomaster
                and not task_gen.env.PROJECTS
        ):
            try:
                mastertask_c = getattr(task_gen, 'mastertasks_c')[-1]
            except AttributeError:
                output = make_bld_node(task_gen, 'src', None, 'master-c-0.%s' % extension)
                mastertask_c = task_gen.create_task('master', [node], [output])
                setattr(task_gen, 'mastertasks_c', [mastertask_c])
                create_compiled_task(task_gen, 'c', output)
            else:
                if len(mastertask_c.inputs) <= 10:
                    mastertask_c.set_inputs([node])
                else:
                    output = make_bld_node(
                        task_gen,
                        'src', None,
                        'master-c-%d.%s' % (
                            len(getattr(task_gen, 'mastertasks_c')), extension)
                    )
                    mastertask_c = task_gen.create_task('master', [node], [output])
                    getattr(task_gen, 'mastertasks_c').append(mastertask_c)
                    create_compiled_task(task_gen, 'c', output)
        else:
            create_compiled_task(task_gen, 'c', node)
    else:
        create_compiled_task(task_gen, 'c', node)


@waflib.TaskGen.extension('.cc', '.cxx', '.cpp', '.mm')
def cc_hook(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    extension = getattr(task_gen, 'objc', False) and 'mm' or 'cc'
    if 'motor:cxx' in task_gen.features:
        category = getattr(task_gen, 'masterfiles').get(node, '')
        if category and not waflib.Options.options.nomaster and not task_gen.env.PROJECTS:
            try:
                mastertask_cxx = getattr(task_gen, 'mastertasks_cxx_%s' % category)
            except AttributeError:
                output = make_bld_node(
                    task_gen,
                    'src',
                    None,
                    'master-cxx-%s.%s' % (category, extension)
                )
                mastertask_cxx = task_gen.create_task('master', [node], [output])
                setattr(task_gen, 'mastertasks_cxx_%s' % category, mastertask_cxx)
                create_compiled_task(task_gen, 'cxx', output)
            else:
                mastertask_cxx.set_inputs([node])
        elif (
                category is not None
                and 'motor:masterfiles:off' not in task_gen.features
                and not waflib.Options.options.nomaster
                and not task_gen.env.PROJECTS
        ):
            try:
                mastertask_cxx = getattr(task_gen, 'mastertasks_cxx')[-1]
            except AttributeError:
                output = make_bld_node(task_gen, 'src', None, 'master-cxx-0.%s' % extension)
                mastertask_cxx = task_gen.create_task('master', [node], [output])
                setattr(task_gen, 'mastertasks_cxx', [mastertask_cxx])
                create_compiled_task(task_gen, 'cxx', output)
            else:
                if len(mastertask_cxx.inputs) <= 10:
                    mastertask_cxx.set_inputs([node])
                else:
                    output = make_bld_node(
                        task_gen,
                        'src', None, 'master-cxx-%d.%s' % (len(getattr(task_gen, 'mastertasks_cxx')), extension)
                    )
                    mastertask_cxx = task_gen.create_task('master', [node], [output])
                    getattr(task_gen, 'mastertasks_cxx').append(mastertask_cxx)
                    create_compiled_task(task_gen, 'cxx', output)
        else:
            create_compiled_task(task_gen, 'cxx', node)
    else:
        create_compiled_task(task_gen, 'cxx', node)


def setup_masterfiles(_: waflib.Build.BuildContext) -> None:
    pass
