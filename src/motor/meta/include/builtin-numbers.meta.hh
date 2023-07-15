/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTIN_NUMBERS_META_HH
#define MOTOR_META_BUILTIN_NUMBERS_META_HH

#include <motor/meta/stdafx.h>

namespace Motor {

struct [[motor::meta(name = "bool")]] motor_bool {};

struct [[motor::meta(name = "u8")]] motor_u8
{
    u8 value;
    [[motor::meta(implicit)]] motor_u8(i64 value) : value(u8(value))
    {
    }
    [[motor::meta(implicit)]] motor_u8(u64 value) : value(u8(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "u16")]] motor_u16
{
    u16 value;
    [[motor::meta(implicit)]] motor_u16(i64 value) : value(u16(value))
    {
    }
    [[motor::meta(implicit)]] motor_u16(u64 value) : value(u16(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "u32")]] motor_u32
{
    u32 value;
    [[motor::meta(implicit)]] motor_u32(i64 value) : value(u32(value))
    {
    }
    [[motor::meta(implicit)]] motor_u32(u64 value) : value(u32(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "u64")]] motor_u64
{
    u64 value;
    [[motor::meta(implicit)]] motor_u64(i64 value) : value(u64(value))
    {
    }
};

struct [[motor::meta(name = "i8")]] motor_i8
{
    i8 value;
    [[motor::meta(implicit)]] motor_i8(i64 value) : value(i8(value))
    {
    }
    [[motor::meta(implicit)]] motor_i8(u64 value) : value(i8(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "i16")]] motor_i16
{
    i16 value;
    [[motor::meta(implicit)]] motor_i16(i64 value) : value(i16(value))
    {
    }
    [[motor::meta(implicit)]] motor_i16(u64 value) : value(i16(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "i32")]] motor_i32
{
    i32 value;
    [[motor::meta(implicit)]] motor_i32(i64 value) : value(i32(value))
    {
    }
    [[motor::meta(implicit)]] motor_i32(u64 value) : value(i32(value))
    {
    }
    [[motor::meta(implicit)]] operator i64() const
    {
        return value;
    }
    [[motor::meta(implicit)]] operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = "i64")]] motor_i64
{
    i64 value;
    [[motor::meta(implicit)]] motor_i64(u64 value) : value(i64(value))
    {
    }
};

struct [[motor::meta(name = "float")]] motor_float
{
    float value;
    [[motor::meta(implicit)]] motor_float(float value) : value(value)
    {
    }
    operator float() const
    {
        return value;
    }
};

struct [[motor::meta(name = "double")]] motor_double
{
    double value;
    [[motor::meta(implicit)]] motor_double(double value) : value(value)
    {
    }
    operator double() const
    {
        return value;
    }
};

}  // namespace Motor

#endif
