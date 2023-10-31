import os
from ...options import SetupContext


def setup_host_windows(setup_context: SetupContext) -> None:
    path = setup_context.bldnode.make_node('host/win32')
    environ = getattr(setup_context, 'environ', os.environ)
    environ['PATH'] = os.pathsep.join([os.path.join(path.abspath(), 'bin'), environ['PATH']])
