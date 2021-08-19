/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <functions.script.hh>
#include <motor/meta/engine/namespace.hh>

namespace Motor { namespace TestCases {

void Class::doStuff(u32 v1, u32 v2, u32 v3)
{
    motor_info("v1: %d | v2: %d | v3: %d" | v1 | v2 | v3);
}

void Class::doStuff(float v1, float v2)
{
    motor_info("v1: %f | v2: %f" | v1 | v2);
}

void Class::doStuff(u32 v1, u32 v2, bool done)
{
    motor_info("v1: %d | v2: %d | done : %s" | v1 | v2 | done);
}

}}  // namespace Motor::TestCases
