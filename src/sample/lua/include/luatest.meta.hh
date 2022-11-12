/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/minitl/tuple.hh>

namespace Motor {

struct LuaTest
{
    minitl::tuple< u8, u16, u32, float > value;
};

}  // namespace Motor
