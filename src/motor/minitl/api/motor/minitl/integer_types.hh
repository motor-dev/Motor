/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < u32 BYTE_COUNT >
struct integer_type;

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

template < u32 BYTE_COUNT >
using signed_integer_type_t = typename integer_type< BYTE_COUNT >::signed_type;
template < u32 BYTE_COUNT >
using unsigned_integer_type_t = typename integer_type< BYTE_COUNT >::unsigned_type;

}  // namespace minitl
