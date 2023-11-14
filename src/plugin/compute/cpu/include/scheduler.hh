/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CPU_SCHEDULER_HH
#define MOTOR_PLUGIN_COMPUTE_CPU_SCHEDULER_HH

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
    weak< Resource::ResourceManager >        m_resourceManager;
    minitl::vector< scoped< KernelLoader > > m_cpuLoaders;
    scoped< MemoryHost >                     m_memoryHost;

public:
    explicit Scheduler(const Plugin::Context& context);
    ~Scheduler() override;

    void run(weak< const Task::KernelTask > task) override;
};

}}}  // namespace Motor::KernelScheduler::CPU

#endif
