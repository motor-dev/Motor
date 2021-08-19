/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CUDA_CUDAKERNELSCHEDULER_HH_
#define MOTOR_COMPUTE_CUDA_CUDAKERNELSCHEDULER_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class CodeLoader;
class MemoryHost;
class CUDAKernelTaskItem;

class Scheduler : public IScheduler
{
private:
    weak< Resource::ResourceManager > m_resourceManager;
    ref< CodeLoader >                 m_cudaLoader;
    scoped< MemoryHost >              m_memoryHost;

public:
    Scheduler(const Plugin::Context& context);
    ~Scheduler();

    virtual IKernelTaskItem*    allocateItem(weak< Task::KernelTask > owner,
                                             weak< const Kernel > kernel, u32 parameterCount) override;
    void                        deallocateItem(CUDAKernelTaskItem* item);
    virtual void                run(IKernelTaskItem* item) override;
    virtual weak< IMemoryHost > memoryHost() const override;
};

}}}  // namespace Motor::KernelScheduler::Cuda

/**************************************************************************************************/
#endif
