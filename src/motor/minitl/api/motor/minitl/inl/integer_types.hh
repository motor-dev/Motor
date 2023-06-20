/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_INTEGER_TYPES_HH
#define MOTOR_MINITL_INL_INTEGER_TYPES_HH
#pragma once

#include <motor/minitl/integer_types.hh>

namespace minitl {

template <>
struct integer_type< 1 >
{
    typedef u8 unsigned_type;
    typedef i8 signed_type;
};

template <>
struct integer_type< 2 >
{
    typedef u16 unsigned_type;
    typedef i16 signed_type;
};

template <>
struct integer_type< 4 >
{
    typedef u32 unsigned_type;
    typedef i32 signed_type;
};

template <>
struct integer_type< 8 >
{
    typedef u64 unsigned_type;
    typedef i64 signed_type;
};

}  // namespace minitl

#endif
