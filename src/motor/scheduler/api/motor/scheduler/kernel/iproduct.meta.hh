/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_IPRODUCT_META_HH_
#define MOTOR_SCHEDULER_KERNEL_IPRODUCT_META_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/meta/typeinfo.hh>
#include <motor/scheduler/kernel/producer.meta.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) IProduct : public minitl::refcountable
{
protected:
    weak< const Producer > m_producer;

protected:
    IProduct(weak< const Producer > producer) : m_producer(producer)
    {
    }

    virtual ~IProduct();

public:
    static raw< Meta::Class > getNamespace();

    weak< const Producer > producer() const
    {
        return m_producer;
    }

    virtual ref< IParameter > createParameter() const = 0;
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
