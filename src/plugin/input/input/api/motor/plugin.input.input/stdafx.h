/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_INPUT_INPUT_STDAFX_H
#define MOTOR_PLUGIN_INPUT_INPUT_STDAFX_H

#include <motor/stdafx.h>

#if defined(building_input)
#    define MOTOR_API_INPUT MOTOR_EXPORT
#elif defined(motor_dll_input)
#    define MOTOR_API_INPUT MOTOR_IMPORT
#else
#    define MOTOR_API_INPUT
#endif

#endif
