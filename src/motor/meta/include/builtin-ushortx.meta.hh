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
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct ushort2
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct ushort3
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct ushort4
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct ushort8
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct ushort16
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

}
#endif
