/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/threads/semaphore.hh>
#include <motor/core/timer.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>
#include <motor/world/world.meta.hh>
#include <motor/world/worldloader.hh>

namespace Motor {

Application::Application(const weak< Resource::ResourceManager >& resourceManager,
                         const weak< Scheduler >& scheduler, const ipath& dataSubDirectory)
    : m_dataFolder(createDataFolder(dataSubDirectory))
    , m_scheduler(scheduler)
    , m_resourceManager(resourceManager)
    , m_pluginContext(resourceManager, m_dataFolder, m_scheduler)
    , m_updateTask(scoped< Task::TaskGroup >::create(Arena::task(), istring("application:update"),
                                                     knl::Colors::Yellow::Yellow))
    , m_producerLoader(scoped< KernelScheduler::ProducerLoader >::create(Arena::game()))
    , m_worldLoader(scoped< World::WorldLoader >::create(Arena::game(), m_updateTask,
                                                         m_producerLoader, m_pluginContext))
    , m_cpuKernelScheduler(inamespace("plugin.compute.cpu"), m_pluginContext)
    , m_tasks(Arena::task())
    , m_forceContinue()
    , m_resourceLoadingCount(0)
    , m_runLoop(i_bool::create(true))
{
    m_resourceManager->attach< KernelScheduler::Producer >(m_producerLoader);
    m_resourceManager->attach< World::World >(m_worldLoader);

    addTask(
        scoped< Task::Task< Task::MethodCaller< Application, &Application::updateResources > > >::
            create(
                Arena::task(), istring("application:update_resource"), knl::Colors::Green::Green,
                scoped< Task::MethodCaller< Application, &Application::updateResources > >::create(
                    Arena::task(), this)));
    addTask(scoped< Task::Task< Task::ProcedureCaller< &Application::frameUpdate > > >::create(
        Arena::task(), istring("application:update_sync"), knl::Colors::Green::Green,
        scoped< Task::ProcedureCaller< &Application::frameUpdate > >::create(Arena::task())));
    registerInterruptions();
}

Application::~Application()
{
    unregisterInterruptions();
    m_resourceManager->detach< World::World >(m_worldLoader);
    m_resourceManager->detach< KernelScheduler::Producer >(m_producerLoader);
}

void Application::addTask(scoped< Task::ITask >&& task)
{
    weak< Task::ITask > weakTask(task);
    m_tasks.emplace_back(UpdateTask({minitl::move(task),
                                     Task::TaskGroup::TaskStartConnection(m_updateTask, weakTask),
                                     Task::TaskGroup::TaskEndConnection(m_updateTask, weakTask)}));
}

void Application::removeTask(const weak< Task::ITask >& task)
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
    m_resourceLoadingCount = motor_checked_numcast< u32 >(resourceCount);
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
