/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_CAST_HH
#define MOTOR_MINITL_CAST_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
class ref;
template < typename T >
class weak;

template < typename U >
inline U* motor_implicit_cast(U* value);

template < typename U, typename T >
inline U* motor_checked_cast(T* value);

template < typename U, typename T >
inline U motor_function_cast(T value);

template < typename U, typename T >
inline U motor_checked_numcast(T value);

}  // namespace minitl

#include <motor/minitl/inl/cast.hh>

#endif
