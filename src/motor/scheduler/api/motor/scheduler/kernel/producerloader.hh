/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCERLOADER_HH_
#define MOTOR_SCHEDULER_KERNEL_PRODUCERLOADER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

#include <motor/resource/loader.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) ProducerLoader : public Resource::ILoader
{
private:
    void load(weak< const Resource::Description > producer, Resource::Resource & resource) override;
    void unload(weak< const Resource::Description > producer, Resource::Resource & resource)
        override;

public:
    ProducerLoader();
    virtual ~ProducerLoader();
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
