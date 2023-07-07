/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_SCHEDULER_HH
#define MOTOR_SCHEDULER_SCHEDULER_HH

#include <motor/scheduler/stdafx.h>
#include <motor/minitl/pool.hh>
#include <motor/minitl/vector.hh>
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
        explicit WorkItem(const weak< Scheduler >& scheduler) : scheduler(scheduler)
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
    void queueTask(const weak< const Task::ITask >&     task,
                   const weak< const Task::IExecutor >& executor, u32 breakdownCount);
    void queueKernel(const weak< const Task::KernelTask >& task);

public:
    Scheduler();
    ~Scheduler() override;

    void mainThreadJoin();
    u32  workerCount() const;
};

}  // namespace Motor

#endif
