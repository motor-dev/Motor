/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_STDAFX_H_
#define MOTOR_SCHEDULER_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/resource/stdafx.h>

#if defined(building_scheduler)
#    define MOTOR_API_SCHEDULER MOTOR_EXPORT
#elif defined(motor_dll_scheduler)
#    define MOTOR_API_SCHEDULER MOTOR_IMPORT
#else
#    define MOTOR_API_SCHEDULER
#endif

#ifndef MOTOR_COMPUTE
namespace Motor { namespace Arena {
motor_api(SCHEDULER) minitl::Allocator& task();
}}  // namespace Motor::Arena
#endif

#define motor_product(x)

/**************************************************************************************************/
#endif
