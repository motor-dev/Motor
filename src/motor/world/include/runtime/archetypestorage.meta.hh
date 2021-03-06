/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_RUNTIME_ARCHETYPESTORAGE_META_HH_
#define MOTOR_WORLD_RUNTIME_ARCHETYPESTORAGE_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/introspect/policy.meta.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>

#include <motor/world/componentregistry.meta.hh>

namespace Motor { namespace World {

class ArchetypeStorage : published KernelScheduler::Producer
{
    published : struct Policy : public Meta::AST::Policy
    {
    private:
        virtual ref< Meta::AST::IntrospectionHint > verify(Meta::AST::DbContext&           context,
                                                           weak< const Meta::AST::Object > object,
                                                           raw< const Meta::Method >       method,
                                                           const Meta::CallInfo&           callInfo,
                                                           u32 argumentThis) const override;
    };

private:
    weak< ComponentRegistry > const                   m_registry;
    minitl::array< raw< const Meta::Class > > const   m_componentClasses;
    minitl::array< ref< KernelScheduler::IProduct > > m_components;

private:
    ref< Runtime >
    createRuntime(weak< const KernelScheduler::ProducerLoader > loader) const override;

    published
        : motor_tag(Policy()) ArchetypeStorage(
              weak< ComponentRegistry >                                         registry,
              const minitl::array< raw< const Meta::Class > >&                  componentClasses,
              const minitl::array< minitl::array< raw< const Meta::Class > > >& archetypes);
    ~ArchetypeStorage();

public:
    ref< KernelScheduler::IProduct > getProduct(u32 index) const;
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
