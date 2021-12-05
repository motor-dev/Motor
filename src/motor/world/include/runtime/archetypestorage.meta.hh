/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_RUNTIME_ARCHETYPESTORAGE_HH_
#define MOTOR_WORLD_RUNTIME_ARCHETYPESTORAGE_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/introspect/introspectionhint.hh>
#include <motor/introspect/simplepolicy.factory.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>

namespace Motor { namespace World {

class ArchetypeStorage : published KernelScheduler::Producer
{
public:
    class IntrospectionHint : public Meta::AST::IntrospectionHint
    {
    public:
        IntrospectionHint(weak< const Meta::AST::Object > owner, raw< const Meta::Method > method,
                          const Meta::CallInfo& callInfo, u32 argumentThis);

        virtual bool getPropertyType(Meta::AST::DbContext& context, const istring propertyName,
                                     Meta::Type& propertyType) const override;
    };

private:
    raw< const Meta::Class > const m_componentClass;

    published : ref< KernelScheduler::IProduct > component;

private:
    ref< Runtime > createRuntime() const override;

    published
        : motor_tag(Meta::AST::SimplePolicy< ArchetypeStorage::IntrospectionHint >())
              ArchetypeStorage(raw< const Meta::Class > componentClass);
    ~ArchetypeStorage();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
