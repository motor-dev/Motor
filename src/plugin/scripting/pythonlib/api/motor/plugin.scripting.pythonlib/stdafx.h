/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_pythonlib)
#    define MOTOR_API_PYTHONLIB MOTOR_EXPORT
#elif defined(motor_dll_pythonlib)
#    define MOTOR_API_PYTHONLIB MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHONLIB
#endif

namespace Motor { namespace Arena {

motor_api(PYTHONLIB) minitl::Allocator& python();

}}  // namespace Motor::Arena
