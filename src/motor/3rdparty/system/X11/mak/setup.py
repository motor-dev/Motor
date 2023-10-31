import build_framework
import waflib.Errors


def setup(setup_context: build_framework.SetupContext) -> None:
    if 'posix' in setup_context.env.VALID_PLATFORMS:
        build_framework.start_msg_setup(setup_context)
        try:
            build_framework.pkg_config(setup_context, 'x11', var='X11')
            setup_context.end_msg('from pkg-config')
        except waflib.Errors.WafError:
            if build_framework.check_lib(
                    setup_context,
                    ['X11'],
                    includepath=['/usr/X11R6/include']
            ):
                setup_context.end_msg('from system')
            else:
                setup_context.end_msg('not found', color='RED')
