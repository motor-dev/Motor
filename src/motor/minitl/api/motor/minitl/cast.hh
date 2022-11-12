/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
class ref;
template < typename T >
class weak;

template < typename U, typename T >
inline U* motor_checked_cast(T* value);

template < typename U, typename T >
inline ref< U > motor_checked_cast(ref< T > value);

template < typename U, typename T >
inline weak< U > motor_checked_cast(weak< T > value);

template < typename U, typename T >
inline weak< U > motor_const_cast(weak< T > value);

template < typename U, typename T >
inline ref< U > motor_const_cast(ref< T > value);

template < typename U, typename T >
inline U motor_function_cast(T value);

template < typename U, typename T >
inline U motor_checked_numcast(T value);

}  // namespace minitl

#include <motor/minitl/inl/cast.inl>
