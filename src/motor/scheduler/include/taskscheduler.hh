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
#include <motor/minitl/pool.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/iexecutor.hh>
#include <taskitem.hh>

namespace Motor {

class Scheduler;

namespace Task {

class TaskScheduler : public minitl::pointer
{
    MOTOR_NOCOPY(TaskScheduler);

public:
    class Worker;

private:
    friend class Worker;
    friend class TaskItem;

    struct TaskPool
    {
        TaskPool(u32 workerCount);
        ~TaskPool();

        void      push(TaskItem* item, u32 count);
        TaskItem* pop();
        void      resize(u32 workerCount);

        u32        m_workerCount;
        Semaphore  m_poolSignal;
        Semaphore  m_poolLock;
        TaskItem** m_taskPool;
        i_u32      m_firstQueued;
        i_u32      m_lastQueued;
        i_u32      m_firstFree;
        u32        m_poolMask;
    };

private:
    minitl::vector< Worker* > m_workers;
    weak< Scheduler >         m_scheduler;
    i_u32                     m_workerCount;
    TaskPool                  m_mainThreadPool;
    TaskPool                  m_workerTaskPool;
    minitl::pool< TaskItem >  m_taskItemPool;
    Semaphore                 m_taskItemAvailable;

public:
    TaskScheduler(weak< Scheduler > scheduler);
    ~TaskScheduler();

    void queue(weak< const ITask > task, weak< const IExecutor > executor, u32 breakdownCount);

    void mainThreadJoin();
    void notifyEnd();
    bool isRunning() const;
    bool taskDone();

    u32 workerCount() const
    {
        return m_workerCount;
    }
};

}  // namespace Task
}  // namespace Motor

/**************************************************************************************************/
#endif
