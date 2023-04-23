/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/meta/engine/namespace.hh>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/kerneltask.hh>
#include <taskscheduler.hh>

namespace Motor {

Scheduler::Scheduler()
    : m_runningTasks(i_u32::create(0))
    , m_running(i_bool::create(true))
    , m_taskScheduler(scoped< Task::TaskScheduler >::create(Arena::task(), this))
    , m_kernelSchedulers(Arena::task())
{
}

Scheduler::~Scheduler()
{
    m_running.set(false);
}

void Scheduler::queueTask(const weak< const Task::ITask >&     task,
                          const weak< const Task::IExecutor >& executor, u32 breakdownCount)
{
    m_taskScheduler->queue(task, executor, breakdownCount);
}

void Scheduler::queueKernel(const weak< const Task::KernelTask >& task)
{
    motor_forceuse(this);
    task->m_targetScheduler->run(task);
}

void Scheduler::mainThreadJoin()
{
    m_taskScheduler->mainThreadJoin();
}

void Scheduler::notifyEnd()
{
    motor_assert(m_runningTasks == 0, "should not notify end when tasks remain to be done");
    motor_info(Log::scheduler(), "no more tasks to run; exiting");
    m_taskScheduler->notifyEnd();
}

u32 Scheduler::workerCount() const
{
    return m_taskScheduler->workerCount();
}

}  // namespace Motor
