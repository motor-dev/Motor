import os
import build_framework
import waflib.Configure
import waflib.Node
import waflib.Task
import waflib.TaskGen
from typing import Any, List, Union


class flex(waflib.Task.Task):
    run_str = '${FLEX} ${FLEXFLAGS} -o${TGT[0].abspath()} ${SRC[0].abspath()}'
    color = 'CYAN'
    ext_in = ['.l', '.ll']
    ext_out = ['.c', '.cc']
    before = ['c', 'cxx']
    shell = False

    def exec_command(self, cmd: Union[str, List[str]], **kw: Any) -> int:
        if isinstance(cmd, list):
            lst = []
            carry = ''
            for a in cmd:
                if a == '-o':
                    carry = a
                else:
                    lst.append(carry + a)
                    carry = ''
            cmd = lst
        env = os.environ.copy()
        env['PATH'] = os.path.split(cmd[0])[0] + os.pathsep + env.get('PATH', '')
        kw['env'] = env

        return self.generator.bld.exec_command(cmd, **kw)


@waflib.TaskGen.extension('.l', '.ll')
def big_flex(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    outs = []
    if node.name.endswith('.ll'):
        out_node = build_framework.make_bld_node(task_gen, 'src', node.parent, node.name[:-2] + 'cc')
    else:
        out_node = build_framework.make_bld_node(task_gen, 'src', node.parent, node.name[:-1] + 'c')
    outs.append(out_node)

    task_gen.create_task('flex', [node], outs)
    getattr(task_gen, 'out_sources').append(outs[0])


def configure(confifuration_context: waflib.Configure.ConfigurationContext) -> None:
    confifuration_context.find_program('flex', var='FLEX', mandatory=True)
