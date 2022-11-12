/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/reflection/stdafx.h>

#if defined(building_settings)
#    define MOTOR_API_SETTINGS MOTOR_EXPORT
#elif defined(motor_dll_settings)
#    define MOTOR_API_SETTINGS MOTOR_IMPORT
#else
#    define MOTOR_API_SETTINGS
#endif
