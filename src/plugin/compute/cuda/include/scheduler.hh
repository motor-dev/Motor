/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    Scheduler(const Plugin::Context& context);
    ~Scheduler();

    virtual void run(weak< const Task::KernelTask > task) override;
};

}}}  // namespace Motor::KernelScheduler::Cuda
