import os
import build_framework
import waflib.TaskGen


def build(build_context: build_framework.BuildContext) -> None:
    if not build_context.env.PROJECTS:
        build_context.recurse(
            os.path.join(build_context.motornode.abspath(), 'mak', 'build_framework', 'build', 'target', 'macos.py')
        )


@waflib.TaskGen.feature('cprogram', 'cxxprogram')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('process_use')
def set_iphone_program_name(_: waflib.TaskGen.task_gen) -> None:
    pass
