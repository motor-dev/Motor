/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CUDA_SCHEDULER_HH
#define MOTOR_PLUGIN_COMPUTE_CUDA_SCHEDULER_HH

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

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
    explicit Scheduler(const Plugin::Context& context);
    ~Scheduler() override;

    void run(weak< const Task::KernelTask > task) override;
};

}}}  // namespace Motor::KernelScheduler::Cuda

#endif
