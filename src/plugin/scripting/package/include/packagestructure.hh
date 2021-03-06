/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PACKAGE_PACKAGE_HH_
#define MOTOR_PACKAGE_PACKAGE_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/core/endianness.hh>

namespace Motor { namespace PackageManager {

struct PackageHeader
{
    u32_l objectCount;
};

}}  // namespace Motor::PackageManager

/**************************************************************************************************/
#endif
