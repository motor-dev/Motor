import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    if 'darwin' in setup_context.env.VALID_PLATFORMS:
        build_framework.start_msg_setup(setup_context)
        if build_framework.check_framework(setup_context, ['Cocoa']):
            setup_context.end_msg('from system')
        else:
            setup_context.end_msg('not found', color='RED')
