/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_NETWORK_STDAFX_H
#define MOTOR_NETWORK_STDAFX_H

#include <motor/core/stdafx.h>

#if defined(building_network)
#    define MOTOR_API_NETWORK MOTOR_EXPORT
#elif defined(motor_dll_network)
#    define MOTOR_API_NETWORK MOTOR_IMPORT
#else
#    define MOTOR_API_NETWORK
#endif

#endif
