/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_UINTX_META_HH_
#define MOTOR_META_BUILTIN_UINTX_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_u32 << 16)))
motor_pod uint2
{
    u32 operator[](u32) const;
    u32& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_u32 << 16)))
motor_pod uint3
{
    u32 operator[](u32) const;
    u32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_u32 << 16)))
motor_pod uint4
{
    u32 operator[](u32) const;
    u32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_u32 << 16)))
motor_pod uint8
{
    u32 operator[](u32) const;
    u32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_u32 << 16)))
motor_pod uint16
{
    u32 operator[](u32) const;
    u32& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
