import os
from ...options import SetupContext


def setup_host_sunos(setup_context: SetupContext) -> None:
    os.environ['LD_NOVERSION'] = '1'
    environ = getattr(setup_context, 'environ', None)
    if environ:
        environ['LD_NOVERSION'] = '1'
