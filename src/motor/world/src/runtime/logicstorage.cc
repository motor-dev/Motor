/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/logicstorage.hh>

#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace World {

static ref< KernelScheduler::Producer >
createProducer(raw< const Meta::Class >                componentClass,
               weak< const KernelScheduler::IProduct > product)
{
    Meta::Value logicComponentTag = componentClass->getTag(motor_class< LogicComponent >());
    if(logicComponentTag)
    {
        raw< const Meta::Class > kernelClass
            = logicComponentTag.as< const LogicComponent& >().kernelClass;
        if(kernelClass)
        {
            if(kernelClass->constructor)
            {
                Meta::Value productValue(product);
                Meta::Value producer = kernelClass->constructor->doCall(&productValue, 1);
                return producer.as< ref< KernelScheduler::Producer > >();
            }
            else
            {
                motor_error_format(Log::world(),
                                   "Kernel task {0} for logic component {1} has no constructor",
                                   kernelClass->fullname(), componentClass->fullname());
                return ref< KernelScheduler::Producer >();
            }
        }
        else
        {
            return ref< KernelScheduler::Producer >();
        }
    }
    else
    {
        motor_error_format(Log::world(),
                           "Component class {0} registered as Logic Component but does not have a "
                           "LogicComponent tag",
                           componentClass->fullname());
        return ref< KernelScheduler::Producer >();
    }
}

LogicStorage::LogicStorage(raw< const Meta::Class >           componentClass,
                           weak< ComponentRegistry::Runtime > registryRuntime)
    : m_componentClass(componentClass)
    , m_componentProduct()
    , m_updateProducer(createProducer(m_componentClass, m_componentProduct))
    , m_registryRuntime(registryRuntime)
{
}

LogicStorage::~LogicStorage()
{
}

}}  // namespace Motor::World
