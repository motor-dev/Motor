/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_SWAP_HH
#define MOTOR_MINITL_SWAP_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
MOTOR_ALWAYS_INLINE void swap(T& a, T& b);

}  // namespace minitl

#include <motor/minitl/inl/swap.hh>

#endif
