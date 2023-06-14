/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_PARAMETERTYPE_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_PARAMETERTYPE_HH

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

#endif
