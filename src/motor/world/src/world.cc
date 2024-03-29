/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/world.meta.hh>

#include <motor/world/componentregistry.meta.hh>
#include <runtime/worldruntime.hh>

namespace Motor { namespace World {

World::World(const ref< ComponentRegistry >&                           registry,
             minitl::vector< weak< const KernelScheduler::IProduct > > products)
    : m_registry(registry)
    , m_products(minitl::move(products))
{
}

World::~World() = default;

scoped< WorldRuntime >
World::createRuntime(const weak< const KernelScheduler::ProducerLoader >& producerLoader,
                     const Plugin::Context&                               context) const
{
    return scoped< WorldRuntime >::create(
        Arena::game(), producerLoader, context, m_products,
        m_registry->getResource(producerLoader).getHandle< ComponentRegistry::Runtime >());
}

}}  // namespace Motor::World
