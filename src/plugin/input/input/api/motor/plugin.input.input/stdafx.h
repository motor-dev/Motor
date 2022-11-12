/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_input)
#    define MOTOR_API_INPUT MOTOR_EXPORT
#elif defined(motor_dll_input)
#    define MOTOR_API_INPUT MOTOR_IMPORT
#else
#    define MOTOR_API_INPUT
#endif
