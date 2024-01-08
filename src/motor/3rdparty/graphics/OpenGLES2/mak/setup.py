import os
import build_framework
import waflib.Errors


def setup(setup_context: build_framework.SetupContext) -> None:
    if setup_context.env.PROJECTS:
        build_framework.start_msg_setup(setup_context)
        setup_context.env['check_OpenGLES2'] = True
        setup_context.env.append_unique(
            'check_OpenGLES2_includes',
            [os.path.join(setup_context.path.parent.abspath(), 'api')]
        )
        setup_context.end_msg('headers for code completion')
    else:
        build_framework.start_msg_setup(setup_context)
        if 'darwin' in setup_context.env.VALID_PLATFORMS:
            if build_framework.check_framework(setup_context, ['OpenGLES']):
                setup_context.end_msg('from system')
            else:
                setup_context.end_msg('not found', color='YELLOW')
        else:
            try:
                build_framework.pkg_config(setup_context, 'glesv2', var='OpenGLES2')
                build_framework.pkg_config(setup_context, 'egl', var='OpenGLES2')
            except waflib.Errors.WafError:
                if build_framework.check_lib(
                        setup_context,
                        ['GLESv2', 'EGL'],
                        var='OpenGLES2',
                        includepath=[os.path.join(setup_context.path.parent.abspath(), 'api')],
                        includes=['GLES2/gl2.h', 'EGL/egl.h'],
                        functions=['glGenFramebuffers', 'eglCreateContext']
                ):
                    setup_context.end_msg('from system')
                else:
                    setup_context.end_msg('not found', color='YELLOW')
            else:
                setup_context.env.SYSTEM_OPENGLES2 = True
                setup_context.end_msg('from pkg-config')
