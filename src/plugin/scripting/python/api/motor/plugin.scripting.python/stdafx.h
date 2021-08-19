/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHON_STDAFX_H_
#define MOTOR_PYTHON_STDAFX_H_
/**************************************************************************************************/

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/stdafx.h>

#if defined(building_python)
#    define MOTOR_API_PYTHON MOTOR_EXPORT
#elif defined(motor_dll_python)
#    define MOTOR_API_PYTHON MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHON
#endif

/**************************************************************************************************/
#endif
