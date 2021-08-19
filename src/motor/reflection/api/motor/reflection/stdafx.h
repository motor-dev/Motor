/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_PARSE_STDAFX_H_
#define MOTOR_META_PARSE_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/introspect/stdafx.h>
#include <motor/meta/stdafx.h>

#if defined(building_reflection)
#    define MOTOR_API_REFLECTION MOTOR_EXPORT
#elif defined(motor_dll_reflection)
#    define MOTOR_API_REFLECTION MOTOR_IMPORT
#else
#    define MOTOR_API_REFLECTION
#endif

/**************************************************************************************************/
#endif
