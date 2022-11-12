/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/type_traits.hh>

namespace minitl {

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

}  // namespace minitl
