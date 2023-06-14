/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_TUPLE_HH
#define MOTOR_MINITL_TUPLE_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

namespace details {

template < int INDEX, typename T, typename... TAIL >
struct tuple_helper;

}  // namespace details

template < typename... T >
struct tuple : public details::tuple_helper< 0, T... >
{
    constexpr tuple() = default;
    constexpr explicit tuple(const T&... args);
    template < typename... ARGS >
    constexpr explicit tuple(ARGS&&... args);
    constexpr tuple(const tuple&) = default;
    constexpr tuple(tuple&&)      = default;       // NOLINT(performance-noexcept-move-constructor)
    template < typename... T1 >
    constexpr tuple(const tuple< T1... >& other);  // NOLINT(google-explicit-constructor)
    template < typename... T1 >
    constexpr tuple(tuple< T1... >&& other);       // NOLINT(google-explicit-constructor)
    ~tuple() = default;

    tuple& operator=(const tuple&) = default;
    tuple& operator=(tuple&&)      = default;  // NOLINT(performance-noexcept-move-constructor)
    template < typename... T1 >
    tuple& operator=(const tuple< T1... >& other);
};

template < typename... T >
constexpr tuple< unwrap_ref_decay_t< T >... > make_tuple(T&&... args);

}  // namespace minitl

#include <motor/minitl/inl/tuple.hh>

#endif
