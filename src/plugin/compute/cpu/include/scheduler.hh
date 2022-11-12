/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeLoader;
class KernelLoader;
class MemoryHost;
class CPUKernelTaskItem;

class Scheduler : public IScheduler
{
private:
    weak< Resource::ResourceManager >     m_resourceManager;
    minitl::vector< ref< KernelLoader > > m_cpuLoaders;
    scoped< MemoryHost >                  m_memoryHost;

public:
    Scheduler(const Plugin::Context& context);
    ~Scheduler();

    virtual void run(weak< const Task::KernelTask > task) override;
};

}}}  // namespace Motor::KernelScheduler::CPU
