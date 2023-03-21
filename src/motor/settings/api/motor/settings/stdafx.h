/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SETTINGS_STDAFX_H_
#define MOTOR_SETTINGS_STDAFX_H_
/**************************************************************************************************/

#include <motor/core/stdafx.h>
#include <motor/meta/stdafx.h>
#include <motor/reflection/stdafx.h>

#if defined(building_settings)
#    define MOTOR_API_SETTINGS MOTOR_EXPORT
#elif defined(motor_dll_settings)
#    define MOTOR_API_SETTINGS MOTOR_IMPORT
#else
#    define MOTOR_API_SETTINGS
#endif

namespace Motor { namespace Log {

motor_api(SETTINGS) weak< Logger > settings();

}}  // namespace Motor::Log

/**************************************************************************************************/
#endif
