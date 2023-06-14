/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_GLES2_STDAFX_H
#define MOTOR_PLUGIN_GRAPHICS_GLES2_STDAFX_H

#include <motor/stdafx.h>

#include <motor/plugin.graphics.3d/stdafx.h>

#ifdef MOTOR_PLATFORM_DARWIN
#    include <OpenGLES/EAGL.h>
#    include <OpenGLES/ES2/gl.h>
#else
#    include <EGL/egl.h>
#    include <GLES2/gl2.h>
#endif

#endif
