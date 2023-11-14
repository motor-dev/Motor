/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_UTILITY_HH
#define MOTOR_MINITL_INL_UTILITY_HH
#pragma once

#include <motor/minitl/utility.hh>

#include <motor/minitl/type_traits.hh>

namespace minitl {

namespace utility_details {

template < u32 COUNT, u32 I, u32... INDICES >
struct make_index_sequence_impl
{
    typedef typename make_index_sequence_impl< COUNT, I + 1, INDICES..., I >::type type;
};

template < u32 COUNT, u32... INDICES >
struct make_index_sequence_impl< COUNT, COUNT, INDICES... >
{
    typedef index_sequence< INDICES... > type;
};

}  // namespace utility_details

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

template < u32 COUNT >
MOTOR_ALWAYS_INLINE constexpr auto make_index_sequence() ->
    typename utility_details::make_index_sequence_impl< COUNT, 0 >::type
{
    return typename utility_details::make_index_sequence_impl< COUNT, 0 >::type();
}

}  // namespace minitl

#endif
