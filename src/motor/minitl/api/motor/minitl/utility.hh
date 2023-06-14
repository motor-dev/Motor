/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_UTILITY_HH
#define MOTOR_MINITL_UTILITY_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/type_traits.hh>

namespace minitl {

template < class T >
MOTOR_ALWAYS_INLINE constexpr remove_reference_t< T >&& move(T&& t) noexcept;

template < class T >
MOTOR_ALWAYS_INLINE constexpr T&& forward(remove_reference_t< T >& t) noexcept;
template < class T >
MOTOR_ALWAYS_INLINE constexpr T&& forward(remove_reference_t< T >&& t) noexcept;

template < int GET, typename T, typename... TAIL, enable_if_t< GET == 0, bool > = false >
MOTOR_ALWAYS_INLINE const T& get(const T& t, const TAIL&...)
{
    return t;
}

template < int GET, typename T, typename... TAIL, enable_if_t< GET != 0, bool > = false >
MOTOR_ALWAYS_INLINE const auto& get(const T& t, const TAIL&... tail)
{
    motor_forceuse(t);
    return get< GET - 1, TAIL... >(tail...);
}

template < u32... INDICES >
struct index_sequence
{
};

}  // namespace minitl

#include <motor/minitl/inl/utility.hh>

#endif
