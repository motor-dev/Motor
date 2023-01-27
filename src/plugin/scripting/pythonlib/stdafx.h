/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHON_STDAFX_H_
#define MOTOR_PYTHON_STDAFX_H_
/**************************************************************************************************/

#include <motor/stdafx.h>

#if defined(building_pythonlib) || defined(building_py_motor)
#    define MOTOR_API_PYTHONLIB MOTOR_EXPORT
#elif defined(pythonlib_dll)
#    define MOTOR_API_PYTHONLIB MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHONLIB
#endif

namespace Motor { namespace Arena {

motor_api(PYTHONLIB) minitl::Allocator& python();

}}  // namespace Motor::Arena

/**************************************************************************************************/
#endif
