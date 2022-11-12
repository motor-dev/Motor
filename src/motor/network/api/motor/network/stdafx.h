/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>

#if defined(building_network)
#    define MOTOR_API_NETWORK MOTOR_EXPORT
#elif defined(motor_dll_network)
#    define MOTOR_API_NETWORK MOTOR_IMPORT
#else
#    define MOTOR_API_NETWORK
#endif
