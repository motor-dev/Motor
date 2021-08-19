/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_OPENCL_SCHEDULER_HH_
#define MOTOR_COMPUTE_OPENCL_SCHEDULER_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/ischeduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Context;
class KernelLoader;
class MemoryHost;
class CLKernelTaskItem;

class motor_api(OPENCL) Scheduler : public IScheduler
{
private:
    ref< Context >                    m_context;
    weak< Resource::ResourceManager > m_resourceManager;
    scoped< KernelLoader >            m_loader;
    scoped< MemoryHost >              m_memoryHost;
    int                               m_errorCode;
    cl_command_queue                  m_commandQueue;

public:
    Scheduler(const Plugin::Context& pluginContext, ref< Context > clContext);
    ~Scheduler();
    virtual IKernelTaskItem*    allocateItem(weak< Task::KernelTask > owner,
                                             weak< const Kernel > kernel, u32 parameterCount) override;
    void                        deallocateItem(CLKernelTaskItem * item);
    virtual void                run(IKernelTaskItem * item) override;
    virtual weak< IMemoryHost > memoryHost() const override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

/**************************************************************************************************/
#endif
