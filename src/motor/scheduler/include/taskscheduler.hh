/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASKSCHEDULER_HH_
#define MOTOR_SCHEDULER_TASKSCHEDULER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/core/threads/event.hh>
#include <motor/core/threads/semaphore.hh>
#include <motor/core/threads/thread.hh>
#include <motor/kernel/interlocked_stack.hh>
#include <motor/kernel/simd.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor {

class Scheduler;

namespace Task {

template < typename Body >
class Task;
class TaskGroup;
class ITaskItem;

class TaskScheduler : public minitl::pointer
{
    MOTOR_NOCOPY(TaskScheduler);

private:
    class Worker;
    friend class Worker;
    friend class ITaskItem;

private:
    minitl::vector< Worker* > m_workers;
    Semaphore                 m_synchro;
    Semaphore                 m_mainThreadSynchro;
    weak< Scheduler >         m_scheduler;

private:  // friend Worker
    minitl::istack< ITaskItem > m_tasks[Scheduler::PriorityCount];
    minitl::istack< ITaskItem > m_mainThreadTasks[Scheduler::PriorityCount];

private:  // friend class ITaskItem, Worker
    ITaskItem* pop(Scheduler::Affinity affinity);
    bool       taskDone();
    bool       hasTasks();
    bool       isRunning();

public:
    TaskScheduler(weak< Scheduler > scheduler);
    ~TaskScheduler();

    void queue(ITaskItem* head, ITaskItem* tail, u32 count);
    void queue(ITaskItem* head, ITaskItem* tail, u32 count, int priority);

    void mainThreadJoin();
    void notifyEnd();

    u32 workerCount() const
    {
        return motor_checked_numcast< u32 >(m_workers.size());
    }
};

}  // namespace Task
}  // namespace Motor

/**************************************************************************************************/
#endif
