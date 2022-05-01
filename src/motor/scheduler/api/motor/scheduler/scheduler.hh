/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_SCHEDULER_HH_
#define MOTOR_SCHEDULER_SCHEDULER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/minitl/array.hh>
#include <motor/minitl/pool.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/task/iexecutor.hh>

namespace Motor {

namespace Task {
class TaskScheduler;
class TaskGroup;
class KernelTask;
}  // namespace Task

namespace KernelScheduler {
class IScheduler;
}

class motor_api(SCHEDULER) Scheduler : public minitl::pointer
{
    MOTOR_NOCOPY(Scheduler);
    friend class Task::TaskGroup;
    friend class Task::TaskScheduler;

public:
    enum Affinity
    {
        WorkerThread = 0,
        MainThread   = 1
    };

private:
    struct WorkItem
    {
        weak< Scheduler > scheduler;
        WorkItem(weak< Scheduler > scheduler_) : scheduler(scheduler_)
        {
            scheduler->m_runningTasks++;
        }
        ~WorkItem()
        {
            if(0 == --scheduler->m_runningTasks) scheduler->notifyEnd();
        }
    };
    friend struct WorkItem;

private:
    i_u32                                                 m_runningTasks;
    i_bool                                                m_running;
    scoped< Task::TaskScheduler >                         m_taskScheduler;
    minitl::vector< weak< KernelScheduler::IScheduler > > m_kernelSchedulers;

private:
    void notifyEnd();

public:
    void queueTask(weak< const Task::ITask > task, weak< const Task::IExecutor > executor,
                   u32 breakdownCount);
    void queueKernel(weak< const Task::KernelTask > task);
    template < typename T >
    inline void* allocateTask();
    template < typename T >
    inline void releaseTask(T * t);

public:
    Scheduler();
    ~Scheduler();

    void mainThreadJoin();
    u32  workerCount() const;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
