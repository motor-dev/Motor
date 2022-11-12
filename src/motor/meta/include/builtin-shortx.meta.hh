/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct short2
{
    i16 operator[](u32) const;
    i16& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct short3
{
    i16 operator[](u32) const;
    i16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct short4
{
    i16 operator[](u32) const;
    i16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct short8
{
    i16 operator[](u32) const;
    i16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct short16
{
    i16 operator[](u32) const;
    i16& operator[](u32);
};

}
#endif
