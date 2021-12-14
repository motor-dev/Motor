/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASK_KERNELTASK_HH_
#define MOTOR_SCHEDULER_TASK_KERNELTASK_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace KernelScheduler {
class Kernel;
class IScheduler;
}}  // namespace Motor::KernelScheduler

namespace Motor {
class Scheduler;
}

namespace Motor { namespace Task {

class motor_api(SCHEDULER) KernelTask : public ITask
{
    MOTOR_NOCOPY(KernelTask);

    friend class ::Motor::Scheduler;

private:
    weak< const KernelScheduler::Kernel > const                m_kernel;
    weak< KernelScheduler::IScheduler >                        m_targetScheduler;
    minitl::array< weak< KernelScheduler::IParameter > > const m_parameters;
    void*                                                      m_schedulerData;

public:
    template < typename Container >
    KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
               Scheduler::Priority priority, weak< const Motor::KernelScheduler::Kernel > kernel,
               const Container& parameters);
    template < typename Iterator >
    KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
               Scheduler::Priority priority, weak< const Motor::KernelScheduler::Kernel > kernel,
               const Iterator& begin, const Iterator& end);
    ~KernelTask();

    virtual void schedule(weak< Scheduler > scheduler) override;

    weak< const KernelScheduler::Kernel > kernel() const
    {
        return m_kernel;
    };
    void* schedulerData(const weak< KernelScheduler::IScheduler >& scheduler) const
    {
        motor_assert(scheduler == m_targetScheduler, "scheduler mismatch");
        return m_schedulerData;
    }
};

}}  // namespace Motor::Task

#include <motor/scheduler/kernel/ischeduler.hh>

namespace Motor { namespace Task {

template < typename Container >
KernelTask::KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
                       Scheduler::Priority                          priority,
                       weak< const Motor::KernelScheduler::Kernel > kernel,
                       const Container&                             parameters)
    : ITask(name, color, priority, Scheduler::WorkerThread)
    , m_kernel(kernel)
    , m_targetScheduler(KernelScheduler::IScheduler::findScheduler(type))
    , m_parameters(Arena::task(), minitl::begin(parameters), minitl::end(parameters))
    , m_schedulerData(m_targetScheduler->createData(this, m_parameters.size()))
{
}

template < typename Iterator >
KernelTask::KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
                       Scheduler::Priority                          priority,
                       weak< const Motor::KernelScheduler::Kernel > kernel, const Iterator& begin,
                       const Iterator& end)
    : ITask(name, color, priority, Scheduler::WorkerThread)
    , m_kernel(kernel)
    , m_targetScheduler(KernelScheduler::IScheduler::findScheduler(type))
    , m_parameters(Arena::task(), begin, end)
    , m_schedulerData(m_targetScheduler->createData(this, m_parameters.size()))
{
}

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
