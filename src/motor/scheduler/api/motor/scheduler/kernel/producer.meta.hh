/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCER_META_HH
#define MOTOR_SCHEDULER_KERNEL_PRODUCER_META_HH

#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.hh>

#include <motor/minitl/array.hh>
#include <motor/minitl/tuple.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class IProduct;
class ProducerLoader;

class Producer;

class motor_api(SCHEDULER) IProduct : public minitl::refcountable
{
protected:
    weak< const Producer > m_producer;

protected:
    explicit IProduct(const weak< const Producer >& producer) : m_producer(producer)
    {
    }

    ~IProduct() override;

public:
    static raw< Meta::Class > getNamespace();

    weak< const Producer > producer() const
    {
        return m_producer;
    }

    virtual ref< IParameter > createParameter() const = 0;
};

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
        Runtime(const ref< Task::ITask >& task, u32 parameterCount);
    };

protected:
    Producer();
    ~Producer() override;

public:
    virtual ref< Runtime > createRuntime(weak< const ProducerLoader > loader) const = 0;
    ref< Task::ITask >     getTask(const weak< const ProducerLoader >& loader) const;
    ref< IParameter >      getParameter(const weak< const ProducerLoader >& loader,
                                        const weak< const IProduct >&       product) const;
};

}}  // namespace Motor::KernelScheduler

#endif
