/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_SWAP_HH
#define MOTOR_MINITL_INL_SWAP_HH
#pragma once

#include <motor/minitl/swap.hh>

#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
MOTOR_ALWAYS_INLINE void swap(T& a, T& b) noexcept
{
    T c = minitl::move(a);
    a   = minitl::move(b);
    b   = minitl::move(c);
}

}  // namespace minitl

#endif
