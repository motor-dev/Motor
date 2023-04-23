/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/scheduler/kernel/producerloader.hh>

namespace Motor {

raw< Meta::Class > motor_motor_Namespace_Motor_KernelScheduler();

}

namespace Motor { namespace KernelScheduler {

IProduct::~IProduct() = default;

raw< Meta::Class > IProduct::getNamespace()
{
    return motor_motor_Namespace_Motor_KernelScheduler();
}

Producer::Runtime::Runtime(const ref< Task::ITask >& task, u32 parameterCount)
    : task(task)
    , parameters(Arena::task(), parameterCount)
    , chain(Arena::task(), parameterCount)
{
}

Producer::Producer() = default;

Producer::~Producer() = default;

ref< Task::ITask > Producer::getTask(const weak< const ProducerLoader >& loader) const
{
    weak< Runtime > runtime = getResource(loader).getRefHandle< Runtime >();
    return runtime->task;
}

ref< IParameter > Producer::getParameter(const weak< const ProducerLoader >& loader,
                                         const weak< const IProduct >&       product) const
{
    weak< Runtime > runtime = getResource(loader).getRefHandle< Runtime >();
    for(const auto& parameter: runtime->parameters)
    {
        if(parameter.first == product) return parameter.second;
    }
    motor_notreached();
    return {};
}

}}  // namespace Motor::KernelScheduler
