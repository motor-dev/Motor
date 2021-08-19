/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASK_KERNELTASK_HH_
#define MOTOR_SCHEDULER_TASK_KERNELTASK_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/kernel.script.hh>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>
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
    friend class ::Motor::Scheduler;
    MOTOR_NOCOPY(KernelTask);

private:
    weak< const KernelScheduler::Kernel > const                m_kernel;
    weak< KernelScheduler::IScheduler >                        m_targetScheduler;
    minitl::array< weak< KernelScheduler::IParameter > > const m_parameters;
    u32                                                        m_subTaskCount;

public:
    KernelTask(istring name, KernelScheduler::SchedulerType type, color32 color,
               Scheduler::Priority priority, weak< const Motor::KernelScheduler::Kernel > kernel,
               minitl::array< weak< KernelScheduler::IParameter > > parameters);
    ~KernelTask();

    virtual void schedule(weak< Scheduler > scheduler) override;
};

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
