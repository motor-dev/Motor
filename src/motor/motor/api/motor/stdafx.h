/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_STDAFX_H_
#define MOTOR_MOTOR_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/plugin/stdafx.h>
#include <motor/resource/stdafx.h>
#include <motor/scheduler/stdafx.h>
#include <motor/world/stdafx.h>

#if defined(building_motor)
#    define MOTOR_API_MOTOR MOTOR_EXPORT
#elif defined(motor_dll_motor)
#    define MOTOR_API_MOTOR MOTOR_IMPORT
#else
#    define MOTOR_API_MOTOR
#endif

/**************************************************************************************************/
#endif
