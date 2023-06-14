/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGESTRUCTURE_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGESTRUCTURE_HH

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/core/endianness.hh>

namespace Motor { namespace PackageManager {

struct PackageHeader
{
    u32_l objectCount;
};

}}  // namespace Motor::PackageManager

#endif
