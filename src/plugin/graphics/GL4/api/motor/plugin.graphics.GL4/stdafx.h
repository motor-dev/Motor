/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_GL4_STDAFX_H
#define MOTOR_PLUGIN_GRAPHICS_GL4_STDAFX_H

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

namespace Motor { namespace Log {

motor_api(GL4) weak< Logger > gl();

}}  // namespace Motor::Log

#endif
