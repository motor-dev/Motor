/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <codeloader.hh>
#include <memoryhost.hh>
#include <scheduler.hh>

#include <kernelobject.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/kernel/kernel.script.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class CUDAKernelTaskItem : public IKernelTaskItem
{
public:
    CUDAKernelTaskItem(weak< Task::KernelTask > owner, weak< const Kernel > kernel,
                       u32 parmaeterCount);
    ~CUDAKernelTaskItem();
};

CUDAKernelTaskItem::CUDAKernelTaskItem(weak< Task::KernelTask > owner, weak< const Kernel > kernel,
                                       u32 parameterCount)
    : IKernelTaskItem(owner, kernel, parameterCount)
{
}

CUDAKernelTaskItem::~CUDAKernelTaskItem()
{
}

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

IKernelTaskItem* Scheduler::allocateItem(weak< Task::KernelTask > owner,
                                         weak< const Kernel > kernel, u32 parameterCount)
{
    return new(Arena::temporary()) CUDAKernelTaskItem(owner, kernel, parameterCount);
}

void Scheduler::deallocateItem(CUDAKernelTaskItem* item)
{
    item->~CUDAKernelTaskItem();
    Arena::temporary().free(item);
}

void Scheduler::run(IKernelTaskItem* item)
{
    // motor_notreached();
    item->owner()->completed(m_scheduler);
    deallocateItem(motor_checked_cast< CUDAKernelTaskItem >(item));
}

weak< IMemoryHost > Scheduler::memoryHost() const
{
    return m_memoryHost;
}

}}}  // namespace Motor::KernelScheduler::Cuda
