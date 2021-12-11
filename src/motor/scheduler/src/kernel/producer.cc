/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/scheduler/kernel/producerloader.hh>

namespace Motor { namespace KernelScheduler {

Producer::Runtime::Runtime(ref< Task::ITask > task, u32 parameterCount)
    : task(task)
    , parameters(Arena::task(), parameterCount)
    , chain(Arena::task(), parameterCount)
{
}

Producer::Producer()
{
}

Producer::~Producer()
{
}

ref< Task::ITask > Producer::getTask(weak< const ProducerLoader > loader) const
{
    weak< Runtime > runtime = getResource(loader).getRefHandle< Runtime >();
    return runtime->task;
}

ref< IParameter > Producer::getParameter(weak< const ProducerLoader > loader,
                                         weak< const IProduct >       product) const
{
    weak< Runtime > runtime = getResource(loader).getRefHandle< Runtime >();
    for(Runtime::ParameterArray::const_iterator it = runtime->parameters.begin();
        it != runtime->parameters.end(); ++it)
    {
        if(it->first == product) return it->second;
    }
    motor_notreached();
    return ref< IParameter >();
}

}}  // namespace Motor::KernelScheduler
