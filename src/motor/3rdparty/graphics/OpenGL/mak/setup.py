import os
import build_framework
import waflib.Errors


def setup(setup_context: build_framework.SetupContext) -> None:
    if not setup_context.env.PROJECTS:
        build_framework.start_msg_setup(setup_context)
        if 'darwin' in setup_context.env.VALID_PLATFORMS:
            if build_framework.check_framework(
                    setup_context, ['OpenGL'],
                    includepath=[os.path.join(setup_context.path.parent.abspath(), 'api')]
            ):
                setup_context.end_msg('from system')
            else:
                setup_context.end_msg('not found', color='YELLOW')
        elif 'windows' in setup_context.env.VALID_PLATFORMS:
            if build_framework.check_lib(
                    setup_context,
                    ['opengl32', 'gdi32'],
                    includes=['windows.h', 'GL/gl.h'],
                    includepath=[os.path.join(setup_context.path.parent.abspath(), 'api')],
                    functions=['glBegin']
            ):
                setup_context.end_msg('from system')
            else:
                setup_context.end_msg('not found', color='YELLOW')
        else:
            try:
                build_framework.pkg_config(setup_context, 'gl', var='OpenGL')
                setup_context.env.append_unique(
                    'check_OpenGL_includes',
                    [os.path.join(setup_context.path.parent.abspath(), 'api')]
                )
            except waflib.Errors.WafError:
                if build_framework.check_lib(
                        setup_context,
                        ['GL'],
                        var='OpenGL',
                        includes=['GL/gl.h'],
                        includepath=[os.path.join(setup_context.path.parent.abspath(), 'api')],
                        functions=['glBegin']
                ):
                    setup_context.end_msg('from system')
                else:
                    setup_context.end_msg('not found', color='YELLOW')
            else:
                setup_context.env.SYSTEM_OPENGL = True
                setup_context.end_msg('from pkg-config')
    else:
        setup_context.env['check_OpenGL'] = True
        setup_context.env.append_unique(
            'check_OpenGL_includes',
            [os.path.join(setup_context.path.parent.abspath(), 'api')]
        )
