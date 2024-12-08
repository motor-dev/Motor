/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/scheduler/kernel/producerloader.hh>

namespace Motor { namespace KernelScheduler {
IProduct::~IProduct() = default;

Producer::Runtime::Runtime(const ref< Task::ITask >& task, u32 parameterCount)
    : task(task)
    , parameters(Arena::task(), parameterCount)
    , chain(Arena::task(), parameterCount)
{
}

Producer::Producer() = default;

Producer::~Producer() = default;

weak< Task::ITask > Producer::getTask(const weak< const ProducerLoader >& loader) const
{
    weak< Runtime > runtime = getResource(loader).getHandle< Runtime >();
    return runtime->task;
}

ref< IParameter > Producer::getParameter(const weak< const ProducerLoader >& loader,
                                         const weak< const IProduct >&       product) const
{
    weak< Runtime > runtime = getResource(loader).getHandle< Runtime >();
    for(const auto& parameter: runtime->parameters)
    {
        if(parameter.first == product) return parameter.second;
    }
    motor_notreached();
    return {};
}

}}  // namespace Motor::KernelScheduler
