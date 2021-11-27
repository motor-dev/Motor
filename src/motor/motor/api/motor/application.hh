/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_APPLICATION_HH_
#define MOTOR_MOTOR_APPLICATION_HH_
/**************************************************************************************************/
#include <motor/stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scriptengine.hh>

namespace Motor {

namespace KernelScheduler {
class IKernelScheduler;
}

namespace World {
class World;
}
class Folder;

class motor_api(MOTOR) Application : public Resource::ILoader
{
    MOTOR_NOCOPY(Application);

private:
    class WorldResource;
    struct UpdateTask
    {
        ref< Task::ITask >                   task;
        Task::TaskGroup::TaskStartConnection start;
        Task::TaskGroup::TaskEndConnection   end;
    };

private:
    ref< Folder > const                                 m_dataFolder;
    weak< Scheduler >                                   m_scheduler;
    weak< Resource::ResourceManager >                   m_resourceManager;
    Plugin::Context const                               m_pluginContext;
    Plugin::Plugin< KernelScheduler::IKernelScheduler > m_cpuKernelScheduler;
    ref< Task::TaskGroup >                              m_updateTask;
    minitl::vector< UpdateTask >                        m_tasks;
    minitl::vector< ref< WorldResource > >              m_worlds;
    Task::ITask::CallbackConnection                     m_forceContinue;
    size_t                                              m_resourceLoadingCount;
    u32                                                 m_worldCount;
    bool                                                m_runLoop;

private:
    void frameUpdate();
    void updateResources();

private:
    virtual void load(weak< const Resource::Description > world, Resource::Resource & resource)
        override;
    virtual void unload(weak< const Resource::Description > /*world*/,
                        Resource::Resource & resource) override;

private:
    void registerInterruptions();
    void unregisterInterruptions();

protected:
    void                   addTask(ref< Task::ITask > task);
    void                   removeTask(ref< Task::ITask > task);
    const Plugin::Context& pluginContext() const
    {
        return m_pluginContext;
    }
    Application(ref< Folder > dataFolder, weak< Resource::ResourceManager > resourceManager,
                weak< Scheduler > scheduler);

    weak< Task::ITask > applicationUpdateTask() const
    {
        return m_updateTask;
    }

public:
    virtual ~Application();

    int  run();
    void finish();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
