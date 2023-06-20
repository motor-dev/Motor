/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_HASH_HH
#define MOTOR_MINITL_INL_HASH_HH
#pragma once

#include <motor/minitl/hash.hh>
#include <stddef.h>
#include <string.h>

namespace minitl {

template < typename T >
struct hash< const T* > : public hash< T* >
{
};

template < typename T >
struct hash< T* >
{
    u32 operator()(const T* t) const
    {
        return u32(uintptr_t(t));
    }
    bool operator()(const T* t1, const T* t2) const
    {
        return t1 == t2;
    }
};

template < typename T >
struct scalar_hash
{
    u32 operator()(T value) const
    {
        return static_cast< T >(value);
    }
    bool operator()(T v1, T v2) const
    {
        return v1 == v2;
    }
};

template <>
struct hash< bool > : public scalar_hash< bool >
{
};

template <>
struct hash< u8 > : public scalar_hash< u8 >
{
};

template <>
struct hash< u16 > : public scalar_hash< u16 >
{
};

template <>
struct hash< u32 > : public scalar_hash< u32 >
{
};

template <>
struct hash< u64 > : public scalar_hash< u64 >
{
};

template <>
struct hash< i8 > : public scalar_hash< i8 >
{
};

template <>
struct hash< i16 > : public scalar_hash< i16 >
{
};

template <>
struct hash< i32 > : public scalar_hash< i32 >
{
};

template <>
struct hash< i64 > : public scalar_hash< i64 >
{
};

}  // namespace minitl

#endif
