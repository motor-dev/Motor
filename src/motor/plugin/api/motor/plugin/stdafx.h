/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PLUGIN_STDAFX_H_
#define MOTOR_PLUGIN_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/filesystem/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/resource/stdafx.h>
#include <motor/scheduler/stdafx.h>

#if defined(building_plugin)
#    define MOTOR_API_PLUGIN MOTOR_EXPORT
#elif defined(motor_dll_plugin)
#    define MOTOR_API_PLUGIN MOTOR_IMPORT
#else
#    define MOTOR_API_PLUGIN
#endif

#ifndef MOTOR_COMPUTE

namespace Motor { namespace Log {

motor_api(PLUGIN) weak< Logger > plugin();

}}  // namespace Motor::Log

#endif

/**************************************************************************************************/
#endif
