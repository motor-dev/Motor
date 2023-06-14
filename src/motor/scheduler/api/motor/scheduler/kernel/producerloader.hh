/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCERLOADER_HH
#define MOTOR_SCHEDULER_KERNEL_PRODUCERLOADER_HH

#include <motor/scheduler/stdafx.h>

#include <motor/resource/loader.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) ProducerLoader : public Resource::ILoader
{
private:
    ref< Task::ITask > m_startTask;

private:
    void load(const weak< const Resource::IDescription >& producer, Resource::Resource& resource)
        override;
    void unload(const weak< const Resource::IDescription >& producer, Resource::Resource& resource)
        override;

    void start();

public:
    ProducerLoader();
    ~ProducerLoader() override;

    ref< Task::ITask > startTask() const
    {
        return m_startTask;
    }
};

}}  // namespace Motor::KernelScheduler

#endif
