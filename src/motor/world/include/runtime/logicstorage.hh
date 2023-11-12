/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_LOGICSTORAGE_HH
#define MOTOR_WORLD_LOGICSTORAGE_HH

#include <motor/world/stdafx.h>

#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/world/componentregistry.meta.hh>

namespace Motor { namespace World {

class LogicStorage : public minitl::pointer
{
private:
    raw< const Meta::Class > const     m_componentClass;
    ref< KernelScheduler::IProduct >   m_componentProduct;
    ref< KernelScheduler::Producer >   m_updateProducer;
    weak< ComponentRegistry::Runtime > m_registryRuntime;

public:
    LogicStorage(raw< const Meta::Class >                  componentClass,
                 const weak< ComponentRegistry::Runtime >& registryRuntime);
    ~LogicStorage() override;
};

}}  // namespace Motor::World

#endif
