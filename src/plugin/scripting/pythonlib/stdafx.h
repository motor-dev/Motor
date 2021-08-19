/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHON_STDAFX_H_
#define MOTOR_PYTHON_STDAFX_H_
/**************************************************************************************************/

#include <motor/stdafx.h>

#if defined(building_python) || defined(building_py_motor)
#    define MOTOR_API_PYTHON MOTOR_EXPORT
#elif defined(python_dll)
#    define MOTOR_API_PYTHON MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHON
#endif

namespace Motor { namespace Arena {

motor_api(PYTHON) minitl::Allocator& python();

}}  // namespace Motor::Arena

/**************************************************************************************************/
#endif
