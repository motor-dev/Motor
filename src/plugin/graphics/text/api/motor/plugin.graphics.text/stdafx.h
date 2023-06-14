/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_STDAFX_H
#define MOTOR_PLUGIN_GRAPHICS_TEXT_STDAFX_H

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_text)
#    define MOTOR_API_TEXT MOTOR_EXPORT
#elif defined(motor_dll_text)
#    define MOTOR_API_TEXT MOTOR_IMPORT
#else
#    define MOTOR_API_TEXT
#endif

namespace Motor { namespace Log {

weak< Logger > text();

}}  // namespace Motor::Log

#endif
