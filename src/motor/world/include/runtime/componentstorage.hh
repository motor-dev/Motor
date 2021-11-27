/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_STORAGE_COMPONENTSTORAGE_HH_
#define MOTOR_WORLD_STORAGE_COMPONENTSTORAGE_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

#include <motor/scheduler/kernel/iproduct.meta.hh>
#include <motor/scheduler/kernel/producer.meta.hh>

namespace Motor { namespace World {

class ComponentStorage : public minitl::refcountable
{
private:
    raw< const Meta::Class > const   m_componentClass;
    ref< KernelScheduler::IProduct > m_componentProduct;
    ref< KernelScheduler::Producer > m_updateProducer;

public:
    ComponentStorage(raw< const Meta::Class > componentClass);
    ~ComponentStorage();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
