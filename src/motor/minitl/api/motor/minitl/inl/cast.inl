/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/features.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/weakptr.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif

namespace minitl {

template < typename U, typename T >
inline U* motor_checked_cast(T* value)
{
    motor_assert(!value || dynamic_cast< U* >(value), "invalid cast from %s to %s, actual type %s"
                                                          | typeid(T).name() | typeid(U).name()
                                                          | typeid(*value).name());
    return static_cast< U* >(value);
}

template < typename U, typename T >
inline ref< U > motor_checked_cast(ref< T > value)
{
    motor_assert(!value || dynamic_cast< U* >(value.operator->()),
                 "invalid cast from ref<%s> to ref<%s>, actual type ref<%s>" | typeid(T).name()
                     | typeid(U).name() | typeid(*value.operator->()).name());
    return ref< U >(static_cast< U* >(value.operator->()));
}

template < typename U, typename T >
inline weak< U > motor_checked_cast(weak< T > value)
{
    motor_assert(!value || dynamic_cast< U* >(value.operator->()),
                 "invalid cast from weak<%s> to weak<%s>, actual type weak<%s>" | typeid(T).name()
                     | typeid(U).name() | typeid(*value.operator->()).name());
    return weak< U >(static_cast< U* >(value.operator->()));
}

template < typename U, typename T >
inline weak< U > motor_const_cast(weak< T > value)
{
    return weak< U >(const_cast< U* >(value.operator->()));
}

template < typename U, typename T >
inline ref< U > motor_const_cast(ref< T > value)
{
    return ref< U >(const_cast< U* >(value.operator->()));
}

template < typename U, typename T >
inline U motor_function_cast(T value)
{
    typedef void (*GenericFunction)();
    return reinterpret_cast< U >(reinterpret_cast< GenericFunction >(value));
}

#if MOTOR_COMPILER_MSVC
#    pragma warning(push)
#    pragma warning(disable : 4800)
#    pragma warning(disable : 4267)
#endif

template < typename U, typename T >
inline U motor_checked_numcast(T value)
{
    motor_assert(static_cast< T >(static_cast< U >(value)) == value,
                 "precision loss during cast from %s to %s" | typeid(T).name() | typeid(U).name());
    return static_cast< U >(value);
}

#if MOTOR_COMPILER_MSVC
#    pragma warning(pop)
#endif
}  // namespace minitl
