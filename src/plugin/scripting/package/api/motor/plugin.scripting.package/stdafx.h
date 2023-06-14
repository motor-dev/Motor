/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_STDAFX_H
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_STDAFX_H

#include <motor/stdafx.h>

#if defined(building_package)
#    define MOTOR_API_PACKAGE MOTOR_EXPORT
#elif defined(motor_dll_package)
#    define MOTOR_API_PACKAGE MOTOR_IMPORT
#else
#    define MOTOR_API_PACKAGE
#endif

#ifndef MOTOR_COMPUTE
namespace Motor {

namespace Arena {

minitl::allocator& package();
minitl::allocator& packageBuilder();

}  // namespace Arena

namespace Log {

weak< Logger > package();
}

}  // namespace Motor
#endif

#endif
