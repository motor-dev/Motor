/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_DEBUG_RUNTIME_STDAFX_H
#define MOTOR_PLUGIN_DEBUG_RUNTIME_STDAFX_H

#include <motor/stdafx.h>

#if defined(building_runtime)
#    define MOTOR_API_RUNTIME MOTOR_EXPORT
#elif defined(motor_dll_runtime)
#    define MOTOR_API_RUNTIME MOTOR_IMPORT
#else
#    define MOTOR_API_RUNTIME
#endif

#endif
