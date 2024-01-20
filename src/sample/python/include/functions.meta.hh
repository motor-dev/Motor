/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SAMPLE_PYTHON_FUNCTIONS_META_HH
#define MOTOR_SAMPLE_PYTHON_FUNCTIONS_META_HH

#include <stdafx.h>

namespace Motor { namespace TestCases {

class TestClass : public minitl::pointer
{
public:
    i32 x1;
    i32 y1;

    explicit TestClass(i32 x1 = 0, i32 y1 = 0) : x1(x1), y1(y1)
    {
    }
    ~TestClass() override = default;

    void doStuff(float v1, float v2 = 5.0f);
    void doStuff(u32 v1, u32 v2, bool done);
    void doStuff(u32 v1, u32 v2 = 5, u32 v3 = 7);
};

struct TestStruct
{
};

enum TestEnum
{
    Value1,
    Value2,
    Value3 = 5
};

}}  // namespace Motor::TestCases

#endif
