/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SAMPLES_PYTHON_FUNCTIONS_META_HH_
#define MOTOR_SAMPLES_PYTHON_FUNCTIONS_META_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace TestCases {

class Class : public minitl::refcountable
{
    published : i32 x1;
    i32             y1;

    Class(u32 x1 = 0, u32 y1 = 0) : x1(x1), y1(y1)
    {
    }
    ~Class()
    {
    }

    void doStuff(float v1, float v2 = 5.0f);
    void doStuff(u32 v1, u32 v2, bool done);
    void doStuff(u32 v1, u32 v2 = 5, u32 v3 = 7);
};

struct Struct
{
};

enum Enum
{
    Value1,
    Value2,
    Value3 = 5
};

}}  // namespace Motor::TestCases

/**************************************************************************************************/
#endif
