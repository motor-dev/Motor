import os
import tempfile
from waflib import Task


def clang_exec_command(exec_command):

    def exec_command_response_file(task, cmd, **kw_args):
        if task.env.COMPILER_NAME == 'clang':
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

    return exec_command_response_file


def build(bld):
    for env in bld.multiarch_envs:
        if env.COMPILER_NAME == 'clang':
            env.ENABLE_COMPILER_DEPS = True
            env.append_unique('CFLAGS', ['-MMD'])
            env.append_unique('CXXFLAGS', ['-MMD'])
    for cls_name in 'c', 'cxx', 'cshlib', 'cxxshlib', 'cprogram', 'cxxprogram':
        cls = Task.classes.get(cls_name, None)
        if not getattr(cls, 'exec_command_patched', False):
            derived = type(cls_name, (cls, ), {})
            derived.exec_command = clang_exec_command(derived.exec_command)
            derived.exec_command_patched = True
