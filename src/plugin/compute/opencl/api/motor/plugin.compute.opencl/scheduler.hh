/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_SCHEDULER_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_SCHEDULER_HH

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
    weak< const Context >             m_context;
    weak< Resource::ResourceManager > m_resourceManager;
    scoped< KernelLoader >            m_loader;
    scoped< MemoryHost >              m_memoryHost;
    int                               m_errorCode;
    cl_command_queue                  m_commandQueue;

public:
    Scheduler(const Plugin::Context& pluginContext, const weak< Context >& clContext);
    ~Scheduler() override;
    void run(weak< const Task::KernelTask > task) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
