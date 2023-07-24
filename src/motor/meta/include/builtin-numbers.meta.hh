/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTIN_NUMBERS_META_HH
#define MOTOR_META_BUILTIN_NUMBERS_META_HH

#include <motor/meta/stdafx.h>

namespace Motor {

struct [[motor::meta(name = bool, interface = bool)]] motor_bool
{
    bool value;
    explicit motor_bool(bool value) : value(value)
    {
    }
    explicit operator bool() const
    {
        return value;
    }
};

struct [[motor::meta(name = u8, interface = u64)]] motor_u8
{
    u8 value;
    explicit motor_u8(u64 value) : value(u8(value))
    {
    }
    explicit operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = u16, interface = u64)]] motor_u16
{
    u16 value;
    explicit motor_u16(u64 value) : value(u16(value))
    {
    }
    explicit operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = u32, interface = u64)]] motor_u32
{
    u32 value;
    explicit motor_u32(u64 value) : value(u32(value))
    {
    }
    explicit operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = u64, interface = u64)]] motor_u64
{
    u64 value;
    explicit motor_u64(i64 value) : value(u64(value))
    {
    }
    explicit operator u64() const
    {
        return value;
    }
};

struct [[motor::meta(name = i8, interface = i64)]] motor_i8
{
    i8 value;
    explicit motor_i8(i64 value) : value(i8(value))
    {
    }
    explicit operator i64() const
    {
        return value;
    }
};

struct [[motor::meta(name = i16, interface = i64)]] motor_i16
{
    i16 value;
    explicit motor_i16(i64 value) : value(i16(value))
    {
    }
    explicit operator i64() const
    {
        return value;
    }
};

struct [[motor::meta(name = i32, interface = i64)]] motor_i32
{
    i32 value;
    explicit motor_i32(i64 value) : value(i32(value))
    {
    }
    explicit operator i64() const
    {
        return value;
    }
};

struct [[motor::meta(name = i64, interface = i64)]] motor_i64
{
    i64 value;
    explicit motor_i64(u64 value) : value(i64(value))
    {
    }
    explicit operator i64() const
    {
        return value;
    }
};

struct [[motor::meta(name = float, interface = float)]] motor_float
{
    float value;
    explicit motor_float(float value) : value(value)
    {
    }
    explicit operator float() const
    {
        return value;
    }
};

struct [[motor::meta(name = double, interface = double)]] motor_double
{
    double value;
    explicit motor_double(double value) : value(value)
    {
    }
    explicit operator double() const
    {
        return value;
    }
};

}  // namespace Motor

#endif
