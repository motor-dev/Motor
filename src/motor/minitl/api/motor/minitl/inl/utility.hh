/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_UTILITY_HH
#define MOTOR_MINITL_INL_UTILITY_HH

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

template < class T >
MOTOR_ALWAYS_INLINE constexpr remove_reference_t< T >&& move(T&& t) noexcept
{
    return static_cast< remove_reference_t< T >&& >(t);
}

template < class T >
MOTOR_ALWAYS_INLINE constexpr T&& forward(remove_reference_t< T >& t) noexcept
{
    return static_cast< T&& >(t);
}

template < class T >
MOTOR_ALWAYS_INLINE constexpr T&& forward(remove_reference_t< T >&& t) noexcept
{
    return static_cast< T&& >(t);
}

template < u32 COUNT >
MOTOR_ALWAYS_INLINE constexpr auto make_index_sequence() ->
    typename utility_details::make_index_sequence_impl< COUNT, 0 >::type
{
    return typename utility_details::make_index_sequence_impl< COUNT, 0 >::type();
}

}  // namespace minitl

#endif
