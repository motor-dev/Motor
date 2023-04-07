/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
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

template < u32 COUNT, u32 I, u32 (&SWIZZLE)[COUNT], u32... INDICES >
struct make_swizzle_sequence_impl
{
    typedef typename make_index_sequence_impl< COUNT, I + 1, INDICES..., SWIZZLE[I] >::type type;
};

template < u32 COUNT, u32 (&SWIZZLE)[COUNT], u32... INDICES >
struct make_swizzle_sequence_impl< COUNT, COUNT, SWIZZLE, INDICES... >
{
    typedef index_sequence< INDICES... > type;
};

}  // namespace utility_details

template < class T >
constexpr remove_reference_t< T >&& move(T&& t) noexcept
{
    return static_cast< remove_reference_t< T >&& >(t);
}

template < class T >
constexpr T&& forward(remove_reference_t< T >& t) noexcept
{
    return static_cast< T&& >(t);
}

template < class T >
constexpr T&& forward(remove_reference_t< T >&& t) noexcept
{
    return static_cast< T&& >(t);
}

template < u32 COUNT >
constexpr auto make_index_sequence() ->
    typename utility_details::make_index_sequence_impl< COUNT, 0 >::type
{
    return typename utility_details::make_index_sequence_impl< COUNT, 0 >::type();
}

template < u32 COUNT, const u32(SWIZZLE)[COUNT] >
constexpr auto make_swizzle_sequence() ->
    typename utility_details::make_swizzle_sequence_impl< COUNT, 0, SWIZZLE >::type
{
    return typename utility_details::make_swizzle_sequence_impl< COUNT, 0, SWIZZLE >::type();
}

}  // namespace minitl
