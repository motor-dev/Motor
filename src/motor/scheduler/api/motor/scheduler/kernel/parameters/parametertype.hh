/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_PARAMETERTYPE_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_PARAMETERTYPE_HH_
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

/**************************************************************************************************/
#endif
