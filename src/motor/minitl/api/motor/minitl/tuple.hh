/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_TUPLE_HH_
#define MOTOR_MINITL_TUPLE_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>

namespace minitl {

namespace details {

template < int INDEX, typename T, typename... TAIL >
struct tuple_helper;
template < u32 INDEX, typename T, typename... TAIL >
struct tuple_type_at_index;

}  // namespace details

template < typename... T >
struct tuple : public details::tuple_helper< 0, T... >
{
    template < u32 INDEX >
    using member_type_t = typename details::tuple_type_at_index< INDEX, T... >::type;

    constexpr tuple() = default;
    constexpr tuple(const T&... args);
    template < typename... Args >
    constexpr tuple(Args&&... args);
    constexpr tuple(const tuple&) = default;
    constexpr tuple(tuple&&)      = default;
    template < typename... T1 >
    constexpr tuple(const tuple< T1... >& other);
    template < typename... T1 >
    constexpr tuple(tuple< T1... >&& other);

    tuple& operator=(const tuple&) = default;
    tuple& operator=(tuple&&)      = default;
    template < typename... T1 >
    tuple& operator=(const tuple< T1... >& other);
};

template < typename... T >
constexpr tuple< unwrap_ref_decay_t< T >... > make_tuple(T&&... args);

}  // namespace minitl

#include <motor/minitl/inl/tuple.inl>

/**************************************************************************************************/
#endif
