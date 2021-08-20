/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CPU_CPUKERNELSCHEDULER_HH_
#define MOTOR_COMPUTE_CPU_CPUKERNELSCHEDULER_HH_
/**************************************************************************************************/
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

    virtual IKernelTaskItem*    allocateItem(weak< Task::KernelTask > owner,
                                             weak< const Kernel > kernel, u32 parameterCount) override;
    void                        deallocateItem(CPUKernelTaskItem* item);
    virtual void                run(IKernelTaskItem* item) override;
    virtual weak< IMemoryHost > memoryHost() const override;
};

}}}  // namespace Motor::KernelScheduler::CPU

/**************************************************************************************************/
#endif
