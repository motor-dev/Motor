/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <codeloader.hh>
#include <kernelloader.hh>
#include <memoryhost.hh>
#include <scheduler.hh>

#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/task/kerneltask.hh>

#include <kernel_variants.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

Scheduler::Scheduler(const Plugin::Context& context)
    : IScheduler(istring("CPU"), context.scheduler, CPUType)
    , m_resourceManager(context.resourceManager)
    , m_cpuLoaders(Arena::task(), s_cpuVariantCount + 1)
    , m_memoryHost(scoped< MemoryHost >::create(Arena::task()))
{
    for(i32 i = 0; i < s_cpuVariantCount; ++i)
    {
        if(*s_cpuVariants[i])
            motor_info_format(Log::cpu(), "registering optimised CPU kernel loader for {0}",
                              s_cpuVariants[i]);
        else
            motor_info(Log::cpu(), "registering unoptimised CPU kernel loader");
        ref< CodeLoader > codeLoader
            = ref< CodeLoader >::create(Arena::task(), inamespace(s_cpuVariants[i]));
        m_cpuLoaders.push_back(ref< KernelLoader >::create(Arena::task(), codeLoader));
        m_resourceManager->attach< Code >(codeLoader);
        m_resourceManager->attach< Kernel >(m_cpuLoaders[i]);
    }
}

Scheduler::~Scheduler()
{
    for(minitl::vector< ref< KernelLoader > >::const_reverse_iterator it = m_cpuLoaders.rbegin();
        it != m_cpuLoaders.rend(); ++it)
    {
        m_resourceManager->detach< Kernel >(*it);
        m_resourceManager->detach< Code >((*it)->codeLoader());
    }
}

void Scheduler::run(weak< const Task::KernelTask > task)
{
    /* TODO: set option to use Neon/AVX/SSE */
    const u32            jobCount = m_scheduler->workerCount() * 4;
    weak< const Kernel > kernel   = task->kernel();
    weak< KernelObject > object
        = kernel->getResource(m_cpuLoaders[0]).getRefHandle< KernelObject >();
    m_scheduler->queueTask(task, object, jobCount);
}

}}}  // namespace Motor::KernelScheduler::CPU
