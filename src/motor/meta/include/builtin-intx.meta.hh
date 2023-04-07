/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace knl
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct int2
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct int3
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct int4
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct int8
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct int16
{
    i32 operator[](u32) const;
    i32& operator[](u32);
};

}
#endif
