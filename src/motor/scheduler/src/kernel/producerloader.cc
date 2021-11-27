/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producerloader.hh>

#include <motor/scheduler/kernel/producer.meta.hh>

namespace Motor { namespace KernelScheduler {

ProducerLoader::ProducerLoader()
{
}

ProducerLoader::~ProducerLoader()
{
}

void ProducerLoader::load(weak< const Resource::Description > producer,
                          Resource::Resource&                 resource)
{
    resource.setRefHandle(motor_checked_cast< const Producer >(producer)->createRuntime());
}

void ProducerLoader::unload(weak< const Resource::Description > producer,
                            Resource::Resource&                 resource)
{
    motor_forceuse(producer);
    resource.clearRefHandle();
}

}}  // namespace Motor::KernelScheduler
