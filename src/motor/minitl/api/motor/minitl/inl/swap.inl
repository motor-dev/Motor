/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_CONTAINER_INL_SWAP_INL_
#define MOTOR_MINITL_CONTAINER_INL_SWAP_INL_
/**************************************************************************************************/
#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T >
void swap(T& a, T& b)
{
    T c = a;
    a   = b;
    b   = c;
}

}  // namespace minitl

/**************************************************************************************************/
#endif
