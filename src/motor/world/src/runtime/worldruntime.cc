/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/worldruntime.hh>

#include <motor/meta/engine/namespace.hh>
#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>

#include <runtime/logicstorage.hh>
#include <subworld.meta.hh>

namespace Motor { namespace World {

WorldRuntime::SubWorldResource::SubWorldResource()
{
}

WorldRuntime::SubWorldResource::~SubWorldResource()
{
}

WorldRuntime::WorldRuntime(weak< const KernelScheduler::ProducerLoader >            producerLoader,
                           const Plugin::Context&                                   context,
                           minitl::array< weak< const KernelScheduler::IProduct > > products,
                           weak< ComponentRegistry::Runtime >                       registryRuntime)
    : m_resourceManager(scoped< Resource::ResourceManager >::create(Arena::game()))
    , m_context(m_resourceManager, context.dataFolder, context.scheduler)
    , m_logicComponentStorage(Arena::game())
    , m_registryRuntime(registryRuntime)
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
    m_productEnds.push_back(Task::ITask::CallbackConnection(
        m_updateTask, producerLoader->startTask()->startCallback()));
    m_productEnds.push_back(
        Task::ITask::CallbackConnection(producerLoader->startTask(), m_eventTask->startCallback()));

    for(minitl::array< weak< const KernelScheduler::IProduct > >::const_iterator product
        = products.begin();
        product != products.end(); ++product)
    {
        m_productEnds.push_back(Task::ITask::CallbackConnection(
            (*product)->producer()->getTask(producerLoader), m_eventTask->startCallback()));
    }
}

WorldRuntime::~WorldRuntime()
{
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

void WorldRuntime::load(weak< const Resource::IDescription > subworld, Resource::Resource& resource)
{
    motor_forceuse(subworld);
    resource.setRefHandle(ref< SubWorldResource >::create(Arena::game()));
}

void WorldRuntime::unload(weak< const Resource::IDescription > subworld,
                          Resource::Resource&                  resource)
{
    motor_forceuse(subworld);
    resource.clearRefHandle();
}

void WorldRuntime::addLogicComponentType(raw< const Meta::Class > type)
{
    m_logicComponentStorage.push_back(
        ref< LogicStorage >::create(Arena::game(), type, m_registryRuntime));
}

void WorldRuntime::spawn(weak< const SubWorld > subworld, u32 parentId,
                         Meta::Value spawnParameters[])
{
    motor_forceuse(parentId);
    motor_forceuse(spawnParameters);
    weak< const SubWorldResource > subworldResource
        = subworld->getResource(this).getRefHandle< SubWorldResource >();
}

}}  // namespace Motor::World
