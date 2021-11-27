/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/runtime/worldruntime.hh>

#include <motor/meta/engine/namespace.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>
#include <motor/world/subworld.meta.hh>

#include <runtime/componentstorage.hh>

namespace Motor { namespace World {

WorldRuntime::WorldRuntime(const Plugin::Context&                                   context,
                           minitl::array< weak< const KernelScheduler::IProduct > > products)
    : m_resourceManager(
        scoped< Resource::ResourceManager >::create(Arena::game(), context.resourceManager))
    , m_context(m_resourceManager, context.dataFolder, context.scheduler)
    , m_logicComponentStorage(Arena::game())
    , m_producerLoader(ref< KernelScheduler::ProducerLoader >::create(Arena::game()))
    , m_updateTask(
          ref< Task::Task< Task::MethodCaller< WorldRuntime, &WorldRuntime::update > > >::create(
              Arena::task(), "world:update", Colors::make(89, 89, 180),
              Task::MethodCaller< WorldRuntime, &WorldRuntime::update >(this)))
    , m_eventTask(
          ref< Task::Task< Task::MethodCaller< WorldRuntime, &WorldRuntime::processEvents > > >::
              create(Arena::task(), "world:processEvents", Colors::make(89, 89, 180),
                     Task::MethodCaller< WorldRuntime, &WorldRuntime::processEvents >(this)))
    , m_productEnds(Arena::task(), products.size() + 1)
{
    m_resourceManager->attach< SubWorld >(this);
    m_resourceManager->attach< KernelScheduler::Producer >(m_producerLoader);
    m_productEnds.push_back(
        Task::ITask::CallbackConnection(m_updateTask, m_eventTask->startCallback()));

    for(minitl::array< weak< const KernelScheduler::IProduct > >::const_iterator product
        = products.begin();
        product != products.end(); ++product)
    {
        m_productEnds.push_back(Task::ITask::CallbackConnection(
            (*product)->producer()->getTask(m_producerLoader), m_eventTask->startCallback()));
    }
}

WorldRuntime::~WorldRuntime()
{
    m_resourceManager->detach< KernelScheduler::Producer >(m_producerLoader);
    m_resourceManager->detach< SubWorld >(this);
}

weak< Task::ITask > WorldRuntime::startUpdateTask() const
{
    return m_updateTask;
}

weak< Task::ITask > WorldRuntime::endUpdateTask() const
{
    return m_eventTask;
}

void WorldRuntime::update()
{
}

void WorldRuntime::processEvents()
{
}

void WorldRuntime::load(weak< const Resource::Description > subworld, Resource::Resource& resource)
{
    motor_forceuse(subworld);
    motor_forceuse(resource);
}

void WorldRuntime::unload(weak< const Resource::Description > subworld,
                          Resource::Resource&                 resource)
{
    motor_forceuse(subworld);
    motor_forceuse(resource);
}

void WorldRuntime::addLogicComponentType(raw< const Meta::Class > type)
{
    m_logicComponentStorage.push_back(ref< ComponentStorage >::create(Arena::game(), type));
}

}}  // namespace Motor::World
