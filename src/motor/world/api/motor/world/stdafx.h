/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_STDAFX_H_
#define MOTOR_WORLD_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/resource/stdafx.h>
#include <motor/scheduler/stdafx.h>

#if defined(building_world)
#    define MOTOR_API_WORLD MOTOR_EXPORT
#elif defined(motor_dll_world)
#    define MOTOR_API_WORLD MOTOR_IMPORT
#else
#    define MOTOR_API_WORLD
#endif

#ifndef MOTOR_COMPUTE
namespace Motor { namespace Arena {
motor_api(WORLD) minitl::Allocator& game();
}}  // namespace Motor::Arena
#endif

/**************************************************************************************************/
#endif
