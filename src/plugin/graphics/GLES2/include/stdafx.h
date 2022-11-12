/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#include <motor/plugin.graphics.3d/stdafx.h>

#ifdef MOTOR_PLATFORM_DARWIN
#    include <OpenGLES/EAGL.h>
#    include <OpenGLES/ES2/gl.h>
#else
#    include <EGL/egl.h>
#    include <GLES2/gl2.h>
#endif
