/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_STORAGE_LOGICSTORAGE_HH_
#define MOTOR_WORLD_STORAGE_LOGICSTORAGE_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

#include <motor/scheduler/kernel/iproduct.meta.hh>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <runtime/componentregistry.meta.hh>

namespace Motor { namespace World {

class LogicStorage : public minitl::refcountable
{
private:
    raw< const Meta::Class > const     m_componentClass;
    ref< KernelScheduler::IProduct >   m_componentProduct;
    ref< KernelScheduler::Producer >   m_updateProducer;
    weak< ComponentRegistry::Runtime > m_registryRuntime;

public:
    LogicStorage(raw< const Meta::Class >           componentClass,
                 weak< ComponentRegistry::Runtime > registryRuntime);
    ~LogicStorage();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
