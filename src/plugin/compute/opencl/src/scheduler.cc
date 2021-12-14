/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin.compute.opencl/memoryhost.hh>
#include <motor/plugin.compute.opencl/scheduler.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/itask.hh>
#include <codeloader.hh>
#include <context.hh>
#include <kernelloader.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

static const int s_profilingMode =
#if MOTOR_OPTIM_LEVEL_AT_MOST(MOTOR_OPTIM_LVEL_PROFILE)
    CL_QUEUE_PROFILING_ENABLE
#else
    0
#endif
    ;

Scheduler::Scheduler(const Plugin::Context& pluginContext, ref< Context > clContext)
    : IScheduler("OpenCL", pluginContext.scheduler, GPUType)
    , m_context(clContext)
    , m_resourceManager(pluginContext.resourceManager)
    , m_loader(scoped< KernelLoader >::create(Arena::task(),
                                              ref< CodeLoader >::create(Arena::task(), m_context)))
    , m_memoryHost(scoped< MemoryHost >::create(Arena::task()))
    , m_errorCode(0)
    , m_commandQueue(clCreateCommandQueue(m_context->m_context, m_context->m_device,
                                          s_profilingMode, &m_errorCode))
{
    if(m_context->m_context)
    {
        m_resourceManager->attach< Code >(m_loader->codeLoader());
        m_resourceManager->attach< Kernel >(weak< Resource::ILoader >(m_loader));
    }
}

Scheduler::~Scheduler()
{
    if(m_context->m_context)
    {
        m_resourceManager->detach< Kernel >(weak< const Resource::ILoader >(m_loader));
        m_resourceManager->detach< Code >(m_loader->codeLoader());
        clReleaseCommandQueue(m_commandQueue);
    }
}

void Scheduler::run(weak< Task::KernelTask > task)
{
    // motor_notreached();
    task->completed(m_scheduler);
}

void* Scheduler::createData(weak< Task::KernelTask > task, u32 parameterCount)
{
    motor_forceuse(task);
    motor_forceuse(parameterCount);
    return 0;
}

void Scheduler::disposeData(void* data)
{
    motor_forceuse(data);
}

}}}  // namespace Motor::KernelScheduler::OpenCL
