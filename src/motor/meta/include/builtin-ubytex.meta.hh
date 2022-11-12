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
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct ubyte2
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct ubyte3
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct ubyte4
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct ubyte8
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct ubyte16
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

}
#endif
