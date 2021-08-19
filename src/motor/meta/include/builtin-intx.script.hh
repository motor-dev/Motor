/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_INTX_SCRIPT_HH_
#define MOTOR_META_BUILTIN_INTX_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.script.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_i32 << 16)))
motor_pod int2
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i32 << 16)))
motor_pod int3
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i32 << 16)))
motor_pod int4
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i32 << 16)))
motor_pod int8
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i32 << 16)))
motor_pod int16
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
