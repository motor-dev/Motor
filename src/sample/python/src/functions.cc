/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/meta/engine/namespace.hh>
#include <functions.meta.hh>

namespace Motor { namespace TestCases {

void Class::doStuff(u32 v1, u32 v2, u32 v3)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1} | v3: {2}", v1, v2, v3);
}

void Class::doStuff(float v1, float v2)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1}", v1, v2);
}

void Class::doStuff(u32 v1, u32 v2, bool done)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1} | done: {2:s}", v1, v2, done);
}

}}  // namespace Motor::TestCases
