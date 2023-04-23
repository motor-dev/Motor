/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/world/stdafx.h>
#include <motor/resource/loader.hh>

#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/group.hh>

#include <motor/world/componentregistry.meta.hh>

namespace Motor { namespace World {

class LogicStorage;
class SubWorld;

class WorldRuntime : public Resource::ILoader
{
private:
    class SubWorldResource : public minitl::refcountable
    {
    public:
        SubWorldResource();
        ~SubWorldResource() override;
    };
    struct SubWorldData
    {
        u32 id {};
    };
    struct ProductRuntime;
    typedef minitl::hashmap< weak< const KernelScheduler::IProduct >,
                             ref< const KernelScheduler::IParameter > >
        ParameterMap;

private:
    scoped< Resource::ResourceManager >               m_resourceManager;
    Plugin::Context                                   m_context;
    minitl::vector< ref< LogicStorage > >             m_logicComponentStorage;
    weak< ComponentRegistry::Runtime >                m_registryRuntime;
    ref< Task::ITask >                                m_updateTask;
    ref< Task::ITask >                                m_eventTask;
    Task::ITask::CallbackConnection                   m_startEvent;
    minitl::vector< Task::ITask::CallbackConnection > m_productEnds;

private:
    void update();
    void processEvents();

private:
    void load(const weak< const Resource::IDescription >& subworld,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& subWorld,
                Resource::Resource&                         resource) override;
    void addLogicComponentType(raw< const Meta::Class > type);

public:
    weak< Task::ITask > startUpdateTask() const;
    weak< Task::ITask > endUpdateTask() const;

    void spawn(const weak< const SubWorld >& subworld, u32 parentId, Meta::Value spawnParameters[]);

public:
    WorldRuntime(const weak< const KernelScheduler::ProducerLoader >&            producerLoader,
                 const Plugin::Context&                                          context,
                 const minitl::array< weak< const KernelScheduler::IProduct > >& products,
                 const weak< ComponentRegistry::Runtime >&                       registryRuntime);
    ~WorldRuntime() override;
};

}}  // namespace Motor::World
