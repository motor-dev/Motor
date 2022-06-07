/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SAMPLE_LUATEST_META_HH_
#define MOTOR_SAMPLE_LUATEST_META_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/minitl/tuple.hh>

namespace Motor {

struct LuaTest
{
    minitl::tuple< u8, u16, u32, float > value;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
