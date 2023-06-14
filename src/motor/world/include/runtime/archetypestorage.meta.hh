/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_ARCHETYPESTORAGE_META_HH
#define MOTOR_WORLD_ARCHETYPESTORAGE_META_HH

#include <motor/world/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/introspect/policy.meta.hh>

#include <motor/world/componentregistry.meta.hh>

namespace Motor { namespace World {

class ArchetypeStorage : published KernelScheduler::Producer
{
    published : struct Policy : public Meta::AST::Policy
    {
    private:
        ref< Meta::AST::IntrospectionHint > verify(Meta::AST::DbContext&           context,
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
              const weak< ComponentRegistry >&                                  registry,
              const minitl::array< raw< const Meta::Class > >&                  componentClasses,
              const minitl::array< minitl::array< raw< const Meta::Class > > >& archetypes);
    ~ArchetypeStorage() override;

public:
    ref< KernelScheduler::IProduct > getProduct(u32 index) const;
};

}}  // namespace Motor::World

#endif
