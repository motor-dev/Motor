/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCER_HH_
#define MOTOR_SCHEDULER_KERNEL_PRODUCER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.meta.hh>

#include <motor/minitl/array.hh>
#include <motor/minitl/tuple.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class ProducerLoader;

class motor_api(SCHEDULER) Producer : public Resource::Description
{
protected:
    class motor_api(SCHEDULER) Runtime : public minitl::refcountable
    {
    public:
        typedef minitl::array< minitl::tuple< weak< const IProduct >, ref< IParameter > > >
            ParameterArray;

    public:
        ref< Task::ITask > const task;
        ParameterArray           parameters;

    public:
        Runtime(ref< Task::ITask > task, u32 parameterCount);
    };

protected:
    Producer();
    virtual ~Producer();

public:
    virtual ref< Runtime > createRuntime() const = 0;
    ref< Task::ITask >     getTask(weak< const ProducerLoader > loader) const;
    ref< IParameter >      getParameter(weak< const ProducerLoader > loader,
                                        weak< const IProduct >       product) const;
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
