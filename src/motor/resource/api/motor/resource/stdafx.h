/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_STDAFX_H_
#define MOTOR_RESOURCE_STDAFX_H_
/**************************************************************************************************/

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
namespace Motor { namespace Arena {
motor_api(RESOURCE) minitl::Allocator& resource();
}}  // namespace Motor::Arena
#endif

/**************************************************************************************************/
#endif
