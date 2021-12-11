/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producerloader.hh>

#include <motor/scheduler/kernel/producer.meta.hh>
#include <motor/scheduler/task/method.hh>

namespace Motor { namespace KernelScheduler {

ProducerLoader::ProducerLoader()
    : m_startTask(
        ref< Task::Task< Task::MethodCaller< ProducerLoader, &ProducerLoader::start > > >::create(
            Arena::task(), "loader:start", Colors::make(89, 89, 180),
            Task::MethodCaller< ProducerLoader, &ProducerLoader::start >(this)))
{
}

ProducerLoader::~ProducerLoader()
{
}

void ProducerLoader::load(weak< const Resource::IDescription > producer,
                          Resource::Resource&                  resource)
{
    resource.setRefHandle(motor_checked_cast< const Producer >(producer)->createRuntime(this));
}

void ProducerLoader::unload(weak< const Resource::IDescription > producer,
                            Resource::Resource&                  resource)
{
    motor_forceuse(producer);
    resource.clearRefHandle();
}

void ProducerLoader::start()
{
}

}}  // namespace Motor::KernelScheduler
