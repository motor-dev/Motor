/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_windowing)
#    define MOTOR_API_WINDOWING MOTOR_EXPORT
#elif defined(motor_dll_windowing)
#    define MOTOR_API_WINDOWING MOTOR_IMPORT
#else
#    define MOTOR_API_WINDOWING
#endif
