/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_WINDOWING_STDAFX_H
#define MOTOR_PLUGIN_GRAPHICS_WINDOWING_STDAFX_H

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_windowing)
#    define MOTOR_API_WINDOWING MOTOR_EXPORT
#elif defined(motor_dll_windowing)
#    define MOTOR_API_WINDOWING MOTOR_IMPORT
#else
#    define MOTOR_API_WINDOWING
#endif

namespace Motor { namespace Log {

motor_api(WINDOWING) weak< Logger > windowing();

}}  // namespace Motor::Log

#endif
