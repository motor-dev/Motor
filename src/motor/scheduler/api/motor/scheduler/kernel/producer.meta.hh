/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.hh>

#include <motor/minitl/array.hh>
#include <motor/minitl/tuple.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class IProduct;
class ProducerLoader;

class motor_api(SCHEDULER) Producer : public Resource::Description< Producer >
{
protected:
    class motor_api(SCHEDULER) Runtime : public minitl::refcountable
    {
    public:
        typedef minitl::array< minitl::tuple< weak< const IProduct >, ref< IParameter > > >
            ParameterArray;

    public:
        ref< Task::ITask > const                          task;
        ParameterArray                                    parameters;
        minitl::vector< Task::ITask::CallbackConnection > chain;

    public:
        Runtime(ref< Task::ITask > task, u32 parameterCount);
    };

protected:
    Producer();
    virtual ~Producer();

public:
    virtual ref< Runtime > createRuntime(weak< const ProducerLoader > loader) const = 0;
    ref< Task::ITask >     getTask(weak< const ProducerLoader > loader) const;
    ref< IParameter >      getParameter(weak< const ProducerLoader > loader,
                                        weak< const IProduct >       product) const;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/iproduct.meta.hh>
