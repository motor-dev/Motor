/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/timer.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>
#include <motor/world/world.meta.hh>

namespace Motor {

class Application::WorldResource : public minitl::refcountable
{
    MOTOR_NOCOPY(WorldResource);

private:
    ref< const World::WorldRuntime > m_worldRuntime;
    Task::ITask::CallbackConnection  m_startSceneUpdate;
    Task::ITask::CallbackConnection  m_endSceneUpdate;

public:
    WorldResource(weak< const KernelScheduler::ProducerLoader > producerLoader,
                  const Plugin::Context& context, weak< const World::World > world,
                  weak< Task::TaskGroup > task);
    ~WorldResource();

    void disconnect();
};

Application::WorldResource::WorldResource(
    weak< const KernelScheduler::ProducerLoader > producerLoader, const Plugin::Context& context,
    weak< const World::World > world, weak< Task::TaskGroup > task)
    : m_worldRuntime(world->createRuntime(producerLoader, context))
    , m_startSceneUpdate(task, m_worldRuntime->startUpdateTask()->startCallback())
    , m_endSceneUpdate(m_worldRuntime->endUpdateTask(), task->startCallback())
{
}

Application::WorldResource::~WorldResource()
{
}

void Application::WorldResource::disconnect()
{
    m_startSceneUpdate = Task::ITask::CallbackConnection();
    m_endSceneUpdate   = Task::ITask::CallbackConnection();
}

Application::Application(ref< Folder >                     dataFolder,
                         weak< Resource::ResourceManager > resourceManager,
                         weak< Scheduler >                 scheduler)
    : ILoader()
    , m_dataFolder(dataFolder)
    , m_scheduler(scheduler)
    , m_resourceManager(resourceManager)
    , m_pluginContext(resourceManager, m_dataFolder, m_scheduler)
    , m_producerLoader(scoped< KernelScheduler::ProducerLoader >::create(Arena::game()))
    , m_cpuKernelScheduler("plugin.compute.cpu", m_pluginContext)
    , m_updateTask(ref< Task::TaskGroup >::create(Arena::task(), "application:update",
                                                  Colors::Yellow::Yellow))
    , m_tasks(Arena::task())
    , m_worlds(Arena::task())
    , m_forceContinue()
    , m_resourceLoadingCount(0)
    , m_worldCount(0)
    , m_runLoop(true)
{
    m_resourceManager->attach< KernelScheduler::Producer >(m_producerLoader);
    m_resourceManager->attach< World::World >(this);

    addTask(ref< Task::Task< Task::MethodCaller< Application, &Application::updateResources > > >::
                create(Arena::task(), "application:update_resource", Colors::Green::Green,
                       Task::MethodCaller< Application, &Application::updateResources >(this)));
    addTask(
        ref< Task::Task< Task::MethodCaller< Application, &Application::frameUpdate > > >::create(
            Arena::task(), "application:update_sync", Colors::Green::Green,
            Task::MethodCaller< Application, &Application::frameUpdate >(this)));
    registerInterruptions();
}

Application::~Application(void)
{
    unregisterInterruptions();
    m_resourceManager->detach< World::World >(this);
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

void Application::load(weak< const Resource::IDescription > desc, Resource::Resource& resource)
{
    m_worldCount++;
    weak< const World::World > world   = motor_checked_cast< const World::World >(desc);
    ref< WorldResource >       runtime = ref< WorldResource >::create(
        Arena::resource(), m_producerLoader, m_pluginContext, world, m_updateTask);
    m_worlds.push_back(runtime);
    resource.setRefHandle(runtime);
}

void Application::unload(weak< const Resource::IDescription > desc, Resource::Resource& resource)
{
    motor_forceuse(desc);
    m_worldCount--;
    if(m_worldCount == 0)
    {
        motor_info("Last World destroyed - stopping application");
    }
    {
        weak< WorldResource > runtime = resource.getRefHandle< WorldResource >();
        for(minitl::vector< ref< WorldResource > >::iterator it = m_worlds.begin();
            it != m_worlds.end(); ++it)
        {
            if(*it == runtime)
            {
                minitl::swap(*it, m_worlds.back());
                m_worlds.pop_back();
                break;
            }
        }
    }
    resource.clearRefHandle();
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
        motor_info("interrupt - stopping application (%d resource loading)"
                   | m_resourceLoadingCount);
        for(minitl::vector< ref< WorldResource > >::iterator it = m_worlds.begin();
            it != m_worlds.end(); ++it)
            (*it)->disconnect();
    }
}

void Application::frameUpdate()
{
    static int   frames     = 0;
    static int   frameCount = 100;
    static float now        = Timer::now();
    if(++frames % frameCount == 0)
    {
        float time = Timer::now();
        float t    = (time - now) / float(frameCount);
        if(t > 10.0f)
        {
            motor_info("Average frame time (%d frames): %d milliseconds" | frameCount | (int)t);
            frameCount = 20;
        }
        else
        {
            t = 1000.0f * t;
            if(t > 10.0f)
            {
                motor_info("Average frame time (%d frames): %d microseconds" | frameCount | (int)t);
                frameCount = 5000;
            }
            else
            {
                motor_info("Average frame time (%d frames): %d nanoseconds" | frameCount
                           | (int)(t * 1000.0f));
                frameCount = 200000;
            }
        }
        now = time;
    }
}

void Application::finish()
{
    m_runLoop = false;
}

}  // namespace Motor
