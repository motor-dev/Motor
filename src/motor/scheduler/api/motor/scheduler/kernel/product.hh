/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCT_HH_
#define MOTOR_SCHEDULER_KERNEL_PRODUCT_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/iproduct.script.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Product : public IProduct
{
public:
    Product(ref< T > parameter, weak< Task::ITask > producer) : IProduct(parameter, producer)
    {
    }

    Product(weak< const Product > other, weak< Task::ITask > producer)
        : IProduct(other->m_parameter, producer)
    {
    }

    ~Product()
    {
    }

public:
    weak< T > parameter() const
    {
        return motor_checked_cast< T >(m_parameter);
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/product.factory.hh>

/**************************************************************************************************/
#endif
