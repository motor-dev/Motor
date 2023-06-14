/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_STDAFX_H
#define MOTOR_RESOURCE_STDAFX_H

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>

#if defined(building_resource)
#    define MOTOR_API_RESOURCE MOTOR_EXPORT
#elif defined(motor_dll_resource)
#    define MOTOR_API_RESOURCE MOTOR_IMPORT
#else
#    define MOTOR_API_RESOURCE
#endif

#ifndef MOTOR_COMPUTE
namespace Motor {

namespace Arena {

motor_api(RESOURCE) minitl::allocator& resource();

}

namespace Log {

motor_api(RESOURCE) weak< Logger > resource();

}

}  // namespace Motor

#endif

#endif
