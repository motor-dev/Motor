/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_IPRODUCT_SCRIPT_HH_
#define MOTOR_SCHEDULER_KERNEL_IPRODUCT_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) IProduct : public minitl::refcountable
{
protected:
    typedef minitl::tuple< weak< IMemoryHost >, u32 > HostInformation;
    ref< IParameter >                                 m_parameter;
    weak< Task::ITask >                               m_producer;
    minitl::vector< HostInformation >                 m_productOutput;

protected:
    IProduct(ref< IParameter > parameter, weak< Task::ITask > producer)
        : m_parameter(parameter)
        , m_producer(producer)
        , m_productOutput(Arena::task())
    {
    }

    virtual ~IProduct();

public:
    static raw< Meta::Class > getNamespace();

    weak< Task::ITask > producer() const
    {
        return m_producer;
    }

    void addOutputHost(weak< IMemoryHost > host);
    void removeOutputHost(weak< IMemoryHost > host);
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
