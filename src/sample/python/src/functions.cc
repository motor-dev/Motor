/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <functions.meta.hh>

namespace Motor { namespace TestCases {

void Class::doStuff(u32 v1, u32 v2, u32 v3)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1} | v3: {2} | x1 {3}", v1, v2, v3, x1);
}

void Class::doStuff(float v1, float v2)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1} | x1 {2}", v1, v2, x1);
}

void Class::doStuff(u32 v1, u32 v2, bool done)
{
    motor_info_format(Log::motor(), "v1: {0} | v2: {1} | done: {2:s} | x1 {3}", v1, v2, done, x1);
}

}}  // namespace Motor::TestCases
