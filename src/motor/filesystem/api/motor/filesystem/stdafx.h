/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_STDAFX_H
#define MOTOR_FILESYSTEM_STDAFX_H

#include <motor/core/stdafx.h>
#include <motor/meta/stdafx.h>

#if defined(building_filesystem)
#    define MOTOR_API_FILESYSTEM MOTOR_EXPORT
#elif defined(motor_dll_filesystem)
#    define MOTOR_API_FILESYSTEM MOTOR_IMPORT
#else
#    define MOTOR_API_FILESYSTEM
#endif

#ifndef MOTOR_COMPUTE
namespace Motor {

namespace Arena {

motor_api(FILESYSTEM) minitl::allocator& filesystem();

}

namespace Log {

motor_api(FILESYSTEM) weak< Logger > fs();

}

}  // namespace Motor
#endif

#endif
