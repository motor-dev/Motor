/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SAMPLE_LUA_LUATEST_META_HH
#define MOTOR_SAMPLE_LUA_LUATEST_META_HH

#include <stdafx.h>
#include <motor/minitl/tuple.hh>

namespace Motor {

struct LuaTest
{
    minitl::tuple< u8, u16, u32, float > value;
};

}  // namespace Motor

#endif
