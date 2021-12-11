/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_RUNTIME_WORLDRUNTIME_HH_
#define MOTOR_WORLD_RUNTIME_WORLDRUNTIME_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/resource/loader.hh>

#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/group.hh>

namespace Motor { namespace World {

class ComponentStorage;

class motor_api(WORLD) WorldRuntime : public Resource::ILoader
{
private:
    struct SubWorldData
    {
        u32 id;
    };
    struct ProductRuntime;
    typedef minitl::hashmap< weak< const KernelScheduler::IProduct >,
                             ref< const KernelScheduler::IParameter > >
        ParameterMap;

private:
    scoped< Resource::ResourceManager >               m_resourceManager;
    Plugin::Context                                   m_context;
    minitl::vector< ref< ComponentStorage > >         m_logicComponentStorage;
    ref< Task::ITask >                                m_updateTask;
    ref< Task::ITask >                                m_eventTask;
    Task::ITask::CallbackConnection                   m_startEvent;
    minitl::vector< Task::ITask::CallbackConnection > m_productEnds;

private:
    void update();
    void processEvents();

private:
    void load(weak< const Resource::IDescription > subworld, Resource::Resource & resource);
    void unload(weak< const Resource::IDescription > subWorld, Resource::Resource & resource);

public:
    weak< Task::ITask > startUpdateTask() const;
    weak< Task::ITask > endUpdateTask() const;
    void                addLogicComponentType(raw< const Meta::Class > type);

public:
    WorldRuntime(weak< const KernelScheduler::ProducerLoader >            producerLoader,
                 const Plugin::Context&                                   context,
                 minitl::array< weak< const KernelScheduler::IProduct > > products);
    ~WorldRuntime();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
