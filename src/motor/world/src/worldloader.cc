/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/worldloader.hh>

#include <motor/world/world.meta.hh>
#include <runtime/worldruntime.hh>

namespace Motor { namespace World {

class WorldLoader::WorldResource : public minitl::refcountable
{
    MOTOR_NOCOPY(WorldResource);

private:
    ref< const WorldRuntime >       m_worldRuntime;
    Task::ITask::CallbackConnection m_startSceneUpdate;
    Task::ITask::CallbackConnection m_endSceneUpdate;

public:
    WorldResource(weak< const KernelScheduler::ProducerLoader > producerLoader,
                  const Plugin::Context& context, weak< const World > world,
                  weak< Task::ITask > task);
    ~WorldResource();

    void disconnect();
};  // namespace Application::WorldResource:publicminitl::refcountable

WorldLoader::WorldResource::WorldResource(
    weak< const KernelScheduler::ProducerLoader > producerLoader, const Plugin::Context& context,
    weak< const World > world, weak< Task::ITask > task)
    : m_worldRuntime(world->createRuntime(producerLoader, context))
    , m_startSceneUpdate(task, m_worldRuntime->startUpdateTask()->startCallback())
    , m_endSceneUpdate(m_worldRuntime->endUpdateTask(), task->startCallback())
{
}

WorldLoader::WorldResource::~WorldResource()
{
}

void WorldLoader::WorldResource::disconnect()
{
    m_startSceneUpdate = Task::ITask::CallbackConnection();
    m_endSceneUpdate   = Task::ITask::CallbackConnection();
}

WorldLoader::WorldLoader(weak< Task::ITask >                     loopTask,
                         weak< KernelScheduler::ProducerLoader > producerLoader,
                         const Plugin::Context&                  pluginContext)
    : ILoader()
    , m_loopTask(loopTask)
    , m_worlds(Arena::task())
    , m_producerLoader(producerLoader)
    , m_pluginContext(pluginContext)
    , m_worldCount(0)
{
}

WorldLoader::~WorldLoader(void)
{
}

void WorldLoader::load(weak< const Resource::IDescription > desc, Resource::Resource& resource)
{
    m_worldCount++;
    weak< const World >  world   = motor_checked_cast< const World >(desc);
    ref< WorldResource > runtime = ref< WorldResource >::create(Arena::resource(), m_producerLoader,
                                                                m_pluginContext, world, m_loopTask);
    m_worlds.push_back(runtime);
    resource.setRefHandle(runtime);
}

void WorldLoader::unload(weak< const Resource::IDescription > desc, Resource::Resource& resource)
{
    motor_forceuse(desc);
    m_worldCount--;
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

void WorldLoader::disconnectWorlds()
{
    for(minitl::vector< ref< WorldResource > >::iterator it = m_worlds.begin();
        it != m_worlds.end(); ++it)
        (*it)->disconnect();
}

}}  // namespace Motor::World
