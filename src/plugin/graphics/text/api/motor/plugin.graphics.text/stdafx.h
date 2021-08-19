/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_STDAFX_H_
#define MOTOR_TEXT_STDAFX_H_
/**************************************************************************************************/

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_text)
#    define MOTOR_API_TEXT MOTOR_EXPORT
#elif defined(motor_dll_text)
#    define MOTOR_API_TEXT MOTOR_IMPORT
#else
#    define MOTOR_API_TEXT
#endif

/**************************************************************************************************/
#endif
