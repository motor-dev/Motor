/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_STDAFX_H
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_STDAFX_H

#include <motor/stdafx.h>

#if defined(building_pythonlib)
#    define MOTOR_API_PYTHONLIB MOTOR_EXPORT
#elif defined(motor_dll_pythonlib)
#    define MOTOR_API_PYTHONLIB MOTOR_IMPORT
#else
#    define MOTOR_API_PYTHONLIB
#endif

namespace Motor {

namespace Arena {

motor_api(PYTHONLIB) minitl::allocator& python();

}

namespace Log {

motor_api(PYTHONLIB) weak< Logger > python();

}

}  // namespace Motor

#endif
