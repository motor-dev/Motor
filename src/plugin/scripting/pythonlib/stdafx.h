/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
