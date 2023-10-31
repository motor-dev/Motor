import os
import waflib.Build


def setup_host_sunos(build_context: waflib.Build.BuildContext) -> None:
    os.environ['LD_NOVERSION'] = '1'
    environ = getattr(build_context, 'environ', None)
    if environ:
        environ['LD_NOVERSION'] = '1'
