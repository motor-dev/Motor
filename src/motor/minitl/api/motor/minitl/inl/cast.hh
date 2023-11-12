/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_CAST_HH
#define MOTOR_MINITL_INL_CAST_HH
#pragma once

#include <motor/minitl/cast.hh>

#include <motor/minitl/assert.hh>
#include <motor/minitl/features.hh>

namespace minitl {

template < typename U >
inline U* motor_implicit_cast(U* value)
{
    return value;
}

template < typename U, typename T >
inline U* motor_checked_cast(T* value)
{
    motor_assert(!value || dynamic_cast< U* >(value), "invalid cast");
    return static_cast< U* >(value);
}

template < typename U, typename T >
inline U motor_function_cast(T value)
{
    typedef void (*generic_function_t)();
    return reinterpret_cast< U >(reinterpret_cast< generic_function_t >(value));
}

#if MOTOR_COMPILER_MSVC
#    pragma warning(push)
#    pragma warning(disable : 4800)
#    pragma warning(disable : 4267)
#endif

template < typename U, typename T >
inline U motor_checked_numcast(T value)
{
    motor_assert(static_cast< T >(static_cast< U >(value)) == value, "precision loss");
    return static_cast< U >(value);
}

#if MOTOR_COMPILER_MSVC
#    pragma warning(pop)
#endif
}  // namespace minitl

#endif
