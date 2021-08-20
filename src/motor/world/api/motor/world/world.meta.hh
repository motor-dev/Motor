/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_WORLD_SCRIPT_HH_
#define MOTOR_WORLD_WORLD_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/core/memory/allocators/system.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/resource/description.meta.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/world/component/storageconfiguration.meta.hh>
#include <motor/world/entity/entity.meta.hh>

namespace Motor { namespace World {

class motor_api(WORLD) World : public Resource::Description
{
private:
    ref< Task::TaskGroup >                              m_task;
    Task::TaskGroup::TaskStartConnection                m_taskStart;
    Task::TaskGroup::TaskEndConnection                  m_taskEnd;
    minitl::array< Task::TaskGroup::TaskEndConnection > m_productEnds;

private:
    void addComponent(Entity e, const void* component, raw< const Meta::Class > metaclass);
    void update();

public:
    weak< Task::ITask > updateWorldTask() const;
    template < typename T >
    void addComponent(Entity e, const T& component)
    {
        addComponent(e, &component, motor_class< T >());
    }
published:
    Entity spawn();
    void   unspawn(Entity e);

    void        addComponent(Entity e, const Meta::Value& v);
    void        removeComponent(Entity e, raw< const Meta::Class > metaclass);
    bool        hasComponent(Entity e, raw< const Meta::Class > metaclass) const;
    Meta::Value getComponent(Entity e, raw< const Meta::Class > metaclass) const;
published:
    World(ref< const Component::StorageConfiguration >             configuration,
          minitl::array< weak< const KernelScheduler::IProduct > > products);
    ~World();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
