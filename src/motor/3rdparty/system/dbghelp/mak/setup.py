import os
import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    if 'windows' in setup_context.env.VALID_PLATFORMS:
        build_framework.start_msg_setup(setup_context)
        if build_framework.check_lib(
                setup_context,
                ['psapi', 'version'],
                includepath=[os.path.join(setup_context.path.parent.abspath(), 'api')],
                includes=['windows.h', 'dbghelp.h'],
        ):
            setup_context.end_msg('from system')
        else:
            setup_context.end_msg('not found', color='RED')
