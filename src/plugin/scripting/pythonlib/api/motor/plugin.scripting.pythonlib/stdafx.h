/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_STDAFX_H_
#define MOTOR_PYTHONLIB_STDAFX_H_
/**************************************************************************************************/

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

/**************************************************************************************************/
#endif
