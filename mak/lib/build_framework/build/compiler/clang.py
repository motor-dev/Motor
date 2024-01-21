import os
import tempfile
import waflib.Task
from ...options import BuildContext
from typing import Any, List


def _wrap_class(cls_name: str) -> None:
    cls = waflib.Task.classes.get(cls_name, None)
    assert cls is not None
    derived = type(cls_name, (cls,), {})

    def exec_command_response_file(task: waflib.Task.Task, cmd: List[str], **kw_args: Any) -> int:
        exec_command = getattr(cls, 'exec_command')
        if task.env.COMPILER_NAME == 'clang':
            if task.env.COMPILER_ABI == 'msvc':
                kw_args['filter_stdout'] = lambda x: x[1:]
            command = []
            resp_file_arguments = []
            inputs = set((x.bldpath() for x in task.inputs))
            for arg in cmd[1:]:
                if arg in inputs:
                    resp_file_arguments.append('"%s"' % arg.replace('\\', '\\\\'))
                elif arg[0:2] in ('-I', '-L', '-D'):
                    resp_file_arguments.append('%s"%s"' % (arg[:2], arg[2:].replace('\\', '\\\\')))
                else:
                    command.append(arg)
            response_file, response_filename = tempfile.mkstemp(dir=task.generator.bld.bldnode.abspath(), text=True)
            try:
                os.write(response_file, '\n'.join(resp_file_arguments).encode())
                os.close(response_file)
                return exec_command(task, [cmd[0], '@%s' % response_filename] + command, **kw_args)
            finally:
                try:
                    os.remove(response_filename)
                except OSError:
                    pass
        else:
            return exec_command(task, cmd, **kw_args)

    setattr(derived, 'exec_command', exec_command_response_file)


def setup_compiler_clang(build_context: BuildContext) -> None:
    for env in build_context.multiarch_envs:
        if env.COMPILER_NAME == 'clang':
            env['ENABLE_COMPILER_DEPS'] = True
            env.append_unique('CFLAGS', ['-MMD'])
            env.append_unique('CXXFLAGS', ['-MMD'])
    for cls_name in 'c', 'cxx', 'cshlib', 'cxxshlib', 'cprogram', 'cxxprogram':
        _wrap_class(cls_name)
