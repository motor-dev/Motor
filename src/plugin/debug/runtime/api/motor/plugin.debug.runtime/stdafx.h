/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_runtime)
#    define MOTOR_API_RUNTIME MOTOR_EXPORT
#elif defined(motor_dll_runtime)
#    define MOTOR_API_RUNTIME MOTOR_IMPORT
#else
#    define MOTOR_API_RUNTIME
#endif
