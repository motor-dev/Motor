/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_FLOATX_META_HH_
#define MOTOR_META_BUILTIN_FLOATX_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_float << 16)))
motor_pod float2
{
    float operator[](u32) const;
    float& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_float << 16)))
motor_pod float3
{
    float operator[](u32) const;
    float& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_float << 16)))
motor_pod float4
{
    float operator[](u32) const;
    float& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_float << 16)))
motor_pod float8
{
    float operator[](u32) const;
    float& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_float << 16)))
motor_pod float16
{
    float operator[](u32) const;
    float& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
