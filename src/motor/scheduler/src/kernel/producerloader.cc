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
            Arena::task(), istring("loader:start"), knl::Colors::make(89, 89, 180),
            scoped< Task::MethodCaller< ProducerLoader, &ProducerLoader::start > >::create(
                Arena::task(), this)))
{
}

ProducerLoader::~ProducerLoader() = default;

void ProducerLoader::load(const weak< const Resource::IDescription >& producer,
                          Resource::Resource&                         resource)
{
    resource.setHandle(motor_checked_cast< const Producer >(producer)->createRuntime(this));
}

void ProducerLoader::unload(const weak< const Resource::IDescription >& producer,
                            Resource::Resource&                         resource)
{
    motor_forceuse(producer);
    resource.clearHandle();
}

void ProducerLoader::start()
{
}

}}  // namespace Motor::KernelScheduler
