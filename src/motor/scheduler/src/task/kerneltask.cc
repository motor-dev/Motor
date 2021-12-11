/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/task/kerneltask.hh>

namespace Motor { namespace Task {

KernelTask::~KernelTask()
{
}

void KernelTask::schedule(weak< Scheduler > scheduler)
{
    scheduler->queueKernel(this, m_parameters);
}

}}  // namespace Motor::Task
