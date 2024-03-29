/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_STDAFX_H
#define MOTOR_PLUGIN_GRAPHICS_3D_STDAFX_H

#include <motor/stdafx.h>

#if defined(building_3d)
#    define MOTOR_API_3D MOTOR_EXPORT
#elif defined(motor_dll_3d)
#    define MOTOR_API_3D MOTOR_IMPORT
#else
#    define MOTOR_API_3D
#endif

namespace Motor { namespace Log {

motor_api(3D) weak< Logger > graphics();
motor_api(3D) weak< Logger > shader();

}}  // namespace Motor::Log

#endif
