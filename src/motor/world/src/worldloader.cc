/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/worldloader.hh>

#include <motor/world/world.meta.hh>
#include <runtime/worldruntime.hh>

namespace Motor { namespace World {

class WorldLoader::WorldResource : public minitl::pointer
{
private:
    scoped< const WorldRuntime >    m_worldRuntime;
    Task::ITask::CallbackConnection m_startSceneUpdate;
    Task::ITask::CallbackConnection m_endSceneUpdate;

public:
    WorldResource(const weak< const KernelScheduler::ProducerLoader >& producerLoader,
                  const Plugin::Context& context, const weak< const World >& world,
                  const weak< Task::ITask >& task);
    ~WorldResource() override;

    void disconnect();
};  // namespace Application::WorldResource:publicminitl::refcountable

WorldLoader::WorldResource::WorldResource(
    const weak< const KernelScheduler::ProducerLoader >& producerLoader,
    const Plugin::Context& context, const weak< const World >& world,
    const weak< Task::ITask >& task)
    : m_worldRuntime(world->createRuntime(producerLoader, context))
    , m_startSceneUpdate(task, m_worldRuntime->startUpdateTask()->startCallback())
    , m_endSceneUpdate(m_worldRuntime->endUpdateTask(), task->startCallback())
{
}

WorldLoader::WorldResource::~WorldResource() = default;

void WorldLoader::WorldResource::disconnect()
{
    m_startSceneUpdate.clear();
    m_endSceneUpdate.clear();
}

WorldLoader::WorldLoader(const weak< Task::ITask >&                     loopTask,
                         const weak< KernelScheduler::ProducerLoader >& producerLoader,
                         Plugin::Context                                pluginContext)
    : ILoader()
    , m_loopTask(loopTask)
    , m_worlds(Arena::task())
    , m_producerLoader(producerLoader)
    , m_pluginContext(minitl::move(pluginContext))
    , m_worldCount(0)
{
}

WorldLoader::~WorldLoader(void) = default;

void WorldLoader::load(const weak< const Resource::IDescription >& worldDescription,
                       Resource::Resource&                         resource)
{
    m_worldCount++;
    weak< const World >     world   = motor_checked_cast< const World >(worldDescription);
    scoped< WorldResource > runtime = scoped< WorldResource >::create(
        Arena::resource(), m_producerLoader, m_pluginContext, world, m_loopTask);
    m_worlds.push_back(runtime);
    resource.setHandle(minitl::move(runtime));
}

void WorldLoader::unload(const weak< const Resource::IDescription >& worldDescription,
                         Resource::Resource&                         resource)
{
    motor_forceuse(worldDescription);
    m_worldCount--;
    {
        weak< WorldResource > runtime = resource.getHandle< WorldResource >();
        for(minitl::vector< weak< WorldResource > >::iterator it = m_worlds.begin();
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
    resource.clearHandle();
}

void WorldLoader::disconnectWorlds()
{
    for(auto& m_world: m_worlds)
        m_world->disconnect();
}

}}  // namespace Motor::World
