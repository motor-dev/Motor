import os
import waflib.Build


def setup_host_windows(build_context: waflib.Build.BuildContext) -> None:
    environ = getattr(build_context, 'environ', os.environ)
    environ['PATH'] = os.pathsep.join(
        [build_context.bldnode.make_node("host/win32/bin").abspath(), environ['PATH']])
    if build_context.env.PATH:
        build_context.env.PATH = [build_context.bldnode.make_node("host/win32/bin").abspath()] + build_context.env.PATH
