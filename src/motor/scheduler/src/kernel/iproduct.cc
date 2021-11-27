/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>

namespace Motor {

raw< Meta::Class > motor_motor_Namespace_Motor_KernelScheduler();

}

namespace Motor { namespace KernelScheduler {

IProduct::~IProduct()
{
}

raw< Meta::Class > IProduct::getNamespace()
{
    return motor_motor_Namespace_Motor_KernelScheduler();
}

}}  // namespace Motor::KernelScheduler
