/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/task/kerneltask.hh>

namespace Motor { namespace Task {

KernelTask::KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
                       Scheduler::Priority                                  priority,
                       weak< const Motor::KernelScheduler::Kernel >         kernel,
                       minitl::array< weak< KernelScheduler::IParameter > > parameters)
    : ITask(name, color, priority, Scheduler::WorkerThread)
    , m_kernel(kernel)
    , m_targetScheduler(KernelScheduler::IScheduler::findScheduler(type))
    , m_parameters(parameters)
{
}

KernelTask::~KernelTask()
{
}

void KernelTask::schedule(weak< Scheduler > scheduler)
{
    scheduler->queueKernel(this, m_parameters);
}

}}  // namespace Motor::Task
