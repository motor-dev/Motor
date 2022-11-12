/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>
#include <motor/scheduler/task/group.hh>

namespace Motor { namespace KernelScheduler {

class IKernelScheduler;
class ProducerLoader;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace World {

class WorldLoader;

}}  // namespace Motor::World

namespace Motor {

class Folder;

class motor_api(MOTOR) Application : public minitl::refcountable
{
    MOTOR_NOCOPY(Application);

private:
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
    ref< Task::TaskGroup >                              m_updateTask;
    scoped< KernelScheduler::ProducerLoader > const     m_producerLoader;
    scoped< World::WorldLoader > const                  m_worldLoader;
    Plugin::Plugin< KernelScheduler::IKernelScheduler > m_cpuKernelScheduler;
    minitl::vector< UpdateTask >                        m_tasks;
    Task::ITask::CallbackConnection                     m_forceContinue;
    size_t                                              m_resourceLoadingCount;
    i_bool                                              m_runLoop;

private:
    void frameUpdate();
    void updateResources();

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
