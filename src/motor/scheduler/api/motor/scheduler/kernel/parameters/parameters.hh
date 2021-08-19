/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_PARAMETERS_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_PARAMETERS_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

namespace Motor { namespace KernelScheduler {

template < typename T >
struct ParamTypeToKernelType
{
    // typedef TODO Type;
};

template < typename T >
struct ParamTypeToKernelType< T* >
{
    // typedef TODO Type;
};

template < typename T >
struct ParamTypeToKernelType< T& >
{
    // typedef TODO Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image1d.hh>
#include <motor/scheduler/kernel/parameters/image2d.hh>
#include <motor/scheduler/kernel/parameters/image3d.hh>
#include <motor/scheduler/kernel/parameters/segment.hh>
#include <motor/scheduler/kernel/parameters/segments.hh>
#include <motor/scheduler/kernel/parameters/stream.hh>

/**************************************************************************************************/
#endif
