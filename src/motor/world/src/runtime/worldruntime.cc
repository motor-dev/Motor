/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/worldruntime.hh>

#include <motor/scheduler/task/group.hh>
#include <motor/scheduler/task/method.hh>

#include <runtime/logicstorage.hh>
#include <subworld.meta.hh>

namespace Motor { namespace World {

WorldRuntime::SubWorldResource::SubWorldResource() = default;

WorldRuntime::SubWorldResource::~SubWorldResource() = default;

WorldRuntime::WorldRuntime(
    const weak< const KernelScheduler::ProducerLoader >&             producerLoader,
    const Plugin::Context&                                           context,
    const minitl::vector< weak< const KernelScheduler::IProduct > >& products,
    const weak< ComponentRegistry::Runtime >&                        registryRuntime)
    : m_resourceManager(scoped< Resource::ResourceManager >::create(Arena::game()))
    , m_context(m_resourceManager, context.dataFolder, context.scheduler)
    , m_logicComponentStorage(Arena::game())
    , m_registryRuntime(registryRuntime)
    , m_updateTask(
          scoped< Task::Task< Task::MethodCaller< WorldRuntime, &WorldRuntime::update > > >::create(
              Arena::task(), istring("world:update"), knl::Colors::make(89, 89, 180),
              scoped< Task::MethodCaller< WorldRuntime, &WorldRuntime::update > >::create(
                  Arena::task(), this)))
    , m_eventTask(
          scoped< Task::Task< Task::MethodCaller< WorldRuntime, &WorldRuntime::processEvents > > >::
              create(Arena::task(), istring("world:processEvents"), knl::Colors::make(89, 89, 180),
                     scoped< Task::MethodCaller< WorldRuntime, &WorldRuntime::processEvents > >::
                         create(Arena::task(), this)))
    , m_productEnds(Arena::task(), products.size() + 1)
{
    m_resourceManager->attach< SubWorld >(this);
    m_productEnds.emplace_back(m_updateTask, producerLoader->startTask()->startCallback());
    m_productEnds.emplace_back(producerLoader->startTask(), m_eventTask->startCallback());

    for(const auto& product: products)
    {
        m_productEnds.emplace_back(product->producer()->getTask(producerLoader),
                                   m_eventTask->startCallback());
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

void WorldRuntime::load(const weak< const Resource::IDescription >& subworld,
                        Resource::Resource&                         resource)
{
    motor_forceuse(subworld);
    resource.setHandle(scoped< SubWorldResource >::create(Arena::game()));
}

void WorldRuntime::unload(const weak< const Resource::IDescription >& subworld,
                          Resource::Resource&                         resource)
{
    motor_forceuse(subworld);
    resource.clearHandle();
}

void WorldRuntime::addLogicComponentType(raw< const Meta::Class > type)
{
    m_logicComponentStorage.push_back(
        scoped< LogicStorage >::create(Arena::game(), type, m_registryRuntime));
}

void WorldRuntime::spawn(const weak< const SubWorld >& subworld, u32 parentId,
                         Meta::Value spawnParameters[])
{
    motor_forceuse(parentId);
    motor_forceuse(spawnParameters);
    weak< const SubWorldResource > subworldResource
        = subworld->getResource(this).getHandle< SubWorldResource >();
}

}}  // namespace Motor::World
