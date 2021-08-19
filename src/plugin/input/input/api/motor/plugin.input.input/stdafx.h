/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_STDAFX_H_
#define MOTOR_INPUT_STDAFX_H_
/**************************************************************************************************/

#include <motor/stdafx.h>

#if defined(building_input)
#    define MOTOR_API_INPUT MOTOR_EXPORT
#elif defined(motor_dll_input)
#    define MOTOR_API_INPUT MOTOR_IMPORT
#else
#    define MOTOR_API_INPUT
#endif

/**************************************************************************************************/
#endif
