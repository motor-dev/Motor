/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>

#include <motor/resource/loader.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) ProducerLoader : public Resource::ILoader
{
private:
    ref< Task::ITask > m_startTask;

private:
    void load(weak< const Resource::IDescription > producer, Resource::Resource & resource)
        override;
    void unload(weak< const Resource::IDescription > producer, Resource::Resource & resource)
        override;

    void start();

public:
    ProducerLoader();
    virtual ~ProducerLoader();

    ref< Task::ITask > startTask() const
    {
        return m_startTask;
    }
};

}}  // namespace Motor::KernelScheduler
