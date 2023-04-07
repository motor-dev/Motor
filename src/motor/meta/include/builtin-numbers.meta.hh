/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>
typedef bool   motor_bool;
typedef float  motor_float;
typedef double motor_double;

#if 0

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_bool << 16)))
motor_tag(Alias("bool"))
struct motor_bool
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_u8 << 16)))
struct u8
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_u16 << 16)))
struct u16
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_u32 << 16)))
struct u32
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_u64 << 16)))
struct u64
{
};


motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_i8 << 16)))
struct i8
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_i16 << 16)))
struct i16
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_i32 << 16)))
struct i32
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_i64 << 16)))
struct i64
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_float << 16)))
motor_tag(Alias("float"))
struct motor_float
{
};

motor_tag(Index(Motor::Meta::ClassType_Number
          + (Motor::Meta::ClassIndex_double << 16)))
motor_tag(Alias("double"))
struct motor_double
{
};

#endif
