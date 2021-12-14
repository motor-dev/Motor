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

void* Scheduler::allocate(size_t size)
{
    if(size > sizeof(Buffer))
        return Arena::task().alloc(size, 1);
    else
        return (void*)m_taskPool.allocate();
}

void Scheduler::release(void* task, size_t size)
{
    if(size > sizeof(Buffer))
        Arena::task().free(task);
    else
        m_taskPool.release((Buffer*)task);
}

Scheduler::Scheduler()
    : m_runningTasks(i_u32::create(0))
    , m_running(i_bool::create(true))
    , m_taskPool(Arena::task(), 65535, 16)
    , m_taskScheduler(scoped< Task::TaskScheduler >::create(Arena::task(), this))
    , m_kernelSchedulers(Arena::task())
{
}

Scheduler::~Scheduler()
{
    m_running = false;
}

void Scheduler::queueTasks(Task::ITaskItem* head, Task::ITaskItem* tail, u32 count,
                           Priority priority)
{
    m_taskScheduler->queue(head, tail, count, priority);
}

void Scheduler::queueTasks(Task::ITaskItem* head, Task::ITaskItem* tail, u32 count)
{
    m_taskScheduler->queue(head, tail, count);
}

void Scheduler::queueKernel(weak< Task::KernelTask > task)
{
    task->m_targetScheduler->run(task);
}

void Scheduler::mainThreadJoin()
{
    m_taskScheduler->mainThreadJoin();
}

void Scheduler::notifyEnd()
{
    motor_assert(m_runningTasks == 0, "should not notify end when tasks remain to be done");
    motor_info("no more tasks to run; exiting");
    m_taskScheduler->notifyEnd();
}

u32 Scheduler::workerCount() const
{
    return m_taskScheduler->workerCount();
}

}  // namespace Motor
