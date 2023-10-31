import os
import build_framework
import waflib.Node
import waflib.Task
import waflib.TaskGen


class bison(waflib.Task.Task):
    run_str = '${BISON} ${BISONFLAGS} ${SRC[0].abspath()} -o ${TGT[0].name}'
    color = 'CYAN'
    ext_in = ['.yc', '.y', '.yy']
    ext_out = '.cxx .h'
    before = 'c cxx flex'

    def post_run(self) -> None:
        source = self.outputs[0]
        header = self.outputs[1]
        try:
            os.stat(header.abspath())
        except OSError:
            try:
                oldheader = source.change_ext(source.suffix() + '.h')
                os.rename(oldheader.abspath(), header.abspath())
            except OSError:
                pass
        waflib.Task.Task.post_run(self)


@waflib.TaskGen.extension('.y', '.yc', '.yy')
def big_bison(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    has_h = '-d' in task_gen.env['BISONFLAGS']

    outs = []
    if node.name.endswith('.yc') or node.name.endswith('.yy'):
        out_node = build_framework.make_bld_node(task_gen, 'src', node.parent, node.name[:-2] + 'cc')
        outs.append(out_node)
        if has_h:
            outs.append(out_node.change_ext('.hh'))
    else:
        out_node = build_framework.make_bld_node(task_gen, 'src', node.parent, node.name[:-1] + 'c')
        outs.append(out_node)
        if has_h:
            outs.append(out_node.change_ext('.h'))

    tsk = task_gen.create_task('bison', [node], outs)
    tsk.cwd = out_node.parent.abspath()

    # and the c/cxx file must be compiled too
    getattr(task_gen, 'out_sources').append(outs[0])


def configure(configuration_context: build_framework.ConfigurationContext) -> None:
    configuration_context.find_program('bison', var='BISON', mandatory=True)
    configuration_context.env['BISONFLAGS'] = '-d'
