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
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct bigint2
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct bigint3
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct bigint4
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct bigint8
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct bigint16
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

}
#endif
