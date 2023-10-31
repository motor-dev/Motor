import os
from ...options import SetupContext


def setup_host_darwin(setup_context: SetupContext) -> None:
    environ = getattr(setup_context, 'environ', os.environ)
    environ['PATH'] = '/System/Library/Frameworks/OpenCL.framework/Libraries:' + environ['PATH']
