/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>

#if defined(building_GL4)
#    define MOTOR_API_GL4 MOTOR_EXPORT
#elif defined(motor_dll_gl4)
#    define MOTOR_API_GL4 MOTOR_IMPORT
#else
#    define MOTOR_API_GL4
#endif

#ifdef MOTOR_PLATFORM_MACOS
#    include <OpenGL/OpenGL.h>
#    include <OpenGL/gl.h>
#    ifndef APIENTRY
#        define APIENTRY
#    endif
#else
#    define GL_GLEXT_PROTOTYPES 1
#    include <GL4/glcorearb.h>
#    include <GL4/glext.h>
#endif
