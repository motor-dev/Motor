/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_UTILITY_HH_
#define MOTOR_MINITL_UTILITY_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/type_traits.hh>

namespace minitl {

template < class T >
constexpr remove_reference_t< T >&& move(T&& t) noexcept;

template < class T >
constexpr T&& forward(remove_reference_t< T >& t) noexcept;
template < class T >
constexpr T&& forward(remove_reference_t< T >&& t) noexcept;

}  // namespace minitl

#include <motor/minitl/inl/utility.inl>

/**************************************************************************************************/
#endif
