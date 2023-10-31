import os
import waflib.Task
import waflib.TaskGen
import waflib.Node
from ...options import BuildContext
from .. import create_compiled_task
from typing import Any, Union, List


class masm(waflib.Task.Task):
    """
    run MASM
    """
    color = 'GREEN'
    run_str = '${ML} /nologo /c /Fo ${TGT[0].abspath()} ${SRC}'


def wrap_class(cls_name: str) -> None:
    cls = waflib.Task.classes.get(cls_name, None)
    if cls is not None:
        derived = type(cls_name, (cls,), {})

        def exec_command_filter(self: waflib.Task.Task, cmd: Union[List[str], str], **kw: Any) -> int:
            if self.env.CC_NAME == 'msvc':
                kw['filter_stdout'] = lambda x: x[1:]
            if self.env.CC_NAME == 'msvc' and os.path.basename(self.env.LINK_CC[0])[0] in ('I', 'X'):
                kw['filter_stderr'] = lambda x: x[1:]
            return getattr(cls, 'exec_command')(self, cmd, **kw)

        setattr(derived, 'exec_command', exec_command_filter)


@waflib.TaskGen.extension('.masm')
def masm_hook(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    if task_gen.env.ML:
        create_compiled_task(task_gen, 'masm', node)


def setup_compiler_msvc(_: BuildContext) -> None:
    for task in 'c', 'cxx', 'cshlib', 'cxxshlib', 'cstlib', 'cxxstlib', 'cprogram', 'cxxprogram', 'masm', 'winrc':
        wrap_class(task)
