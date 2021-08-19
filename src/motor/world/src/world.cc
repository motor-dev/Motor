/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/meta/engine/namespace.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>
#include <motor/world/world.script.hh>

namespace Motor { namespace World {

World::World(ref< const Component::StorageConfiguration >             configuration,
             minitl::array< weak< const KernelScheduler::IProduct > > products)
    : m_task(
        ref< Task::TaskGroup >::create(Arena::task(), "world:update", Colors::make(89, 89, 180)))
    , m_taskStart(m_task, configuration->updateStart())
    , m_productEnds(Arena::task(), products.size() + 1)
{
    minitl::array< Task::TaskGroup::TaskEndConnection >::iterator connection
        = m_productEnds.begin();
    for(minitl::array< weak< const KernelScheduler::IProduct > >::const_iterator product
        = products.begin();
        product != products.end(); ++product, ++connection)
    {
        *connection = Task::TaskGroup::TaskEndConnection(m_task, (*product)->producer());
    }
    m_productEnds.last() = Task::TaskGroup::TaskEndConnection(m_task, configuration->updateStart());
}

World::~World()
{
}

weak< Task::ITask > World::updateWorldTask() const
{
    return m_task;
}

Entity World::spawn()
{
    Entity result = {42};
    return result;
}

void World::unspawn(Entity e)
{
    motor_forceuse(e);
}

void World::addComponent(Entity e, const void* component, raw< const Meta::Class > componentType)
{
    motor_forceuse(e);
    motor_forceuse(component);
    motor_forceuse(componentType);
}

void World::removeComponent(Entity e, raw< const Meta::Class > componentType)
{
    motor_forceuse(e);
    motor_forceuse(componentType);
}

bool World::hasComponent(Entity e, raw< const Meta::Class > componentType) const
{
    motor_forceuse(e);
    motor_forceuse(componentType);
    return false;
}

void World::addComponent(Entity e, const Meta::Value& component)
{
    motor_forceuse(e);
    motor_forceuse(component);
}

Meta::Value World::getComponent(Entity e, raw< const Meta::Class > metaclass) const
{
    motor_forceuse(e);
    motor_forceuse(metaclass);
    return Meta::Value();
}

}}  // namespace Motor::World
