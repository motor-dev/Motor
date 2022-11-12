/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/core/endianness.hh>

namespace Motor { namespace PackageManager {

struct PackageHeader
{
    u32_l objectCount;
};

}}  // namespace Motor::PackageManager
