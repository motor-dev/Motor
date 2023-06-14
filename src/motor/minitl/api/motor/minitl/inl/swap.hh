/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_SWAP_HH
#define MOTOR_MINITL_INL_SWAP_HH

#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T >
MOTOR_ALWAYS_INLINE void swap(T& a, T& b)
{
    T c = a;
    a   = b;
    b   = c;
}

}  // namespace minitl

#endif
