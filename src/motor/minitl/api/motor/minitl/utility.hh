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

template < int GET, typename T, typename... TAIL, enable_if_t< GET == 0, bool > = false >
const T& get(const T& t, const TAIL&... tail)
{
    motor_forceuse_pack(tail);
    return t;
}

template < int GET, typename T, typename... TAIL, enable_if_t< GET != 0, bool > = false >
const auto& get(const T& t, const TAIL&... tail)
{
    motor_forceuse(t);
    return get< GET - 1, TAIL... >(tail...);
}

template < u32... INDICES >
struct index_sequence
{
};

}  // namespace minitl

#include <motor/minitl/inl/utility.inl>

/**************************************************************************************************/
#endif
