/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/threads/semaphore.hh>
#include <motor/core/timer.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>
#include <motor/world/world.meta.hh>
#include <motor/world/worldloader.hh>

namespace Motor {

Application::Application(ref< Folder >                     dataFolder,
                         weak< Resource::ResourceManager > resourceManager,
                         weak< Scheduler >                 scheduler)
    : m_dataFolder(dataFolder)
    , m_scheduler(scheduler)
    , m_resourceManager(resourceManager)
    , m_pluginContext(resourceManager, m_dataFolder, m_scheduler)
    , m_updateTask(ref< Task::TaskGroup >::create(Arena::task(), "application:update",
                                                  Colors::Yellow::Yellow))
    , m_producerLoader(scoped< KernelScheduler::ProducerLoader >::create(Arena::game()))
    , m_worldLoader(scoped< World::WorldLoader >::create(Arena::game(), m_updateTask,
                                                         m_producerLoader, m_pluginContext))
    , m_cpuKernelScheduler("plugin.compute.cpu", m_pluginContext)
    , m_tasks(Arena::task())
    , m_forceContinue()
    , m_resourceLoadingCount(0)
    , m_runLoop(i_bool::create(true))
{
    m_resourceManager->attach< KernelScheduler::Producer >(m_producerLoader);
    m_resourceManager->attach< World::World >(m_worldLoader);

    addTask(
        ref< Task::Task< Task::MethodCaller< Application, &Application::updateResources > > >::
            create(Arena::task(), "application:update_resource", Colors::Green::Green,
                   ref< Task::MethodCaller< Application, &Application::updateResources > >::create(
                       Arena::task(), this)));
    addTask(
        ref< Task::Task< Task::MethodCaller< Application, &Application::frameUpdate > > >::create(
            Arena::task(), "application:update_sync", Colors::Green::Green,
            ref< Task::MethodCaller< Application, &Application::frameUpdate > >::create(
                Arena::task(), this)));
    registerInterruptions();
}

Application::~Application(void)
{
    unregisterInterruptions();
    m_resourceManager->detach< World::World >(m_worldLoader);
    m_resourceManager->detach< KernelScheduler::Producer >(m_producerLoader);
}

void Application::addTask(ref< Task::ITask > task)
{
    UpdateTask t;
    t.task  = task;
    t.start = Task::TaskGroup::TaskStartConnection(m_updateTask, task);
    t.end   = Task::TaskGroup::TaskEndConnection(m_updateTask, task);
    m_tasks.push_back(t);
}

void Application::removeTask(ref< Task::ITask > task)
{
    for(size_t i = 0; i < m_tasks.size(); ++i)
    {
        if(m_tasks[i].task == task)
        {
            minitl::swap(m_tasks[i], m_tasks.back());
            m_tasks.pop_back();
        }
    }
}

int Application::run()
{
    m_updateTask->schedule(m_scheduler);
    m_scheduler->mainThreadJoin();
    return 0;
}

void Application::updateResources()
{
    size_t resourceCount = m_resourceManager->updateTickets();
    if(resourceCount == 0 && m_resourceLoadingCount != 0)
    {
        m_forceContinue = Task::ITask::CallbackConnection();
    }
    else if(resourceCount != 0 && m_resourceLoadingCount == 0)
    {
        m_forceContinue
            = Task::ITask::CallbackConnection(m_updateTask, m_updateTask->startCallback());
    }
    m_resourceLoadingCount = resourceCount;
    if(!m_runLoop)
    {
        motor_info_format(Log::system(),
                          "interrupt - stopping application ({0} resource(s) loading)",
                          m_resourceLoadingCount);
        m_worldLoader->disconnectWorlds();
    }
}

void Application::frameUpdate()
{
    static int   frames     = 0;
    static int   frameCount = 100;
    static float now        = Timer::now();
    if(++frames % frameCount == 0)
    {
        float time       = Timer::now();
        float t          = (time - now) / float(frameCount);
        u32   pauseCount = Semaphore::flushPauseCount() / frameCount;
        if(t > 10.0f)
        {
            motor_info_format(Log::system(),
                              "Average frame time ({0} frames): {1} milliseconds / {2} pauses",
                              frameCount, (int)t, pauseCount);
            frameCount = 20;
        }
        else
        {
            t = 1000.0f * t;
            if(t > 10.0f)
            {
                motor_info_format(Log::system(),
                                  "Average frame time ({0} frames): {1} microseconds / {2} pauses",
                                  frameCount, (int)t, pauseCount);
                frameCount = 5000;
            }
            else
            {
                motor_info_format(Log::system(),
                                  "Average frame time ({0} frames): {1} nanoseconds / {2} pauses",
                                  frameCount, (int)(t * 1000.0f), pauseCount);
                frameCount = 200000;
            }
        }
        now = time;
    }
}

void Application::finish()
{
    m_runLoop.set(false);
}

}  // namespace Motor
