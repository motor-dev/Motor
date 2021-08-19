/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_KERNEL_CL_INPUT_SEGMENTS_HH_
#define MOTOR_KERNEL_CL_INPUT_SEGMENTS_HH_
/**************************************************************************************************/
#include <motor/kernel/stdafx.h>
#include <motor/kernel/input/segment.hh>

namespace Kernel {

template < typename T >
struct segments : public segment< T >
{
};

}  // namespace Kernel

/**************************************************************************************************/
#endif
