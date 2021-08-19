/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_KERNEL_CUDA_INPUT_SEGMENTS_HH_
#define MOTOR_KERNEL_CUDA_INPUT_SEGMENTS_HH_
/**************************************************************************************************/
#include    <motor/kernel/input/segment.hh>
#include    <motor/kernel/stdafx.h>


namespace Kernel
{

template< typename T >
struct segments : public segment<T>
{
};


}

/**************************************************************************************************/
#endif
