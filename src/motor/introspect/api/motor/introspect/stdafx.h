/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_STDAFX_H_
#define MOTOR_INTROSPECT_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>

#if defined(building_introspect)
#    define MOTOR_API_INTROSPECT MOTOR_EXPORT
#elif defined(motor_dll_introspect)
#    define MOTOR_API_INTROSPECT MOTOR_IMPORT
#else
#    define MOTOR_API_INTROSPECT
#endif

/**************************************************************************************************/
#endif
