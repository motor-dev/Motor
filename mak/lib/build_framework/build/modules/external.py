import os
from ...options import BuildContext


def external(build_context: BuildContext,
             name: str) -> str:
    namespace = name.split('.')
    script_file = os.path.join('/'.join(namespace), 'mak', 'build.py')
    if os.path.isfile(os.path.join(build_context.path.abspath(), script_file)):
        build_context.recurse(script_file)
    else:
        build_context.recurse(os.path.join(build_context.motornode.abspath(), 'src', script_file))
    return name
