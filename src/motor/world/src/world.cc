/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/world.meta.hh>

namespace Motor { namespace World {

World::World(minitl::array< weak< const KernelScheduler::IProduct > > products)
    : m_products(products)
{
}

World::~World()
{
}

ref< WorldRuntime > World::createRuntime(const Plugin::Context& context) const
{
    return ref< WorldRuntime >::create(Arena::game(), context, m_products);
}

}}  // namespace Motor::World
