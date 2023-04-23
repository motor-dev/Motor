/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <codeloader.hh>
#include <memoryhost.hh>
#include <scheduler.hh>

#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/task/kerneltask.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

Scheduler::Scheduler(const Plugin::Context& context)
    : IScheduler("Cuda", context.scheduler, GPUType)
    , m_resourceManager(context.resourceManager)
    , m_cudaLoader(ref< CodeLoader >::create(Arena::task()))
    , m_memoryHost(scoped< MemoryHost >::create(Arena::task()))
{
    m_resourceManager->attach< Kernel >(m_cudaLoader);
}

Scheduler::~Scheduler()
{
    m_resourceManager->detach< Kernel >(m_cudaLoader);
}

void Scheduler::run(weak< const Task::KernelTask > task)
{
    // motor_notreached();
    task->completed(m_scheduler);
}

}}}  // namespace Motor::KernelScheduler::Cuda
