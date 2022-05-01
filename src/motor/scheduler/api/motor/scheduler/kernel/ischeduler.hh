/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_ISCHEDULER_HH_
#define MOTOR_SCHEDULER_KERNEL_ISCHEDULER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>

#include <motor/minitl/array.hh>

namespace Motor {
class Scheduler;
}

namespace Motor { namespace Task {

class KernelTask;

}}  // namespace Motor::Task

namespace Motor { namespace KernelScheduler {

class IParameter;

class motor_api(SCHEDULER) IScheduler : public minitl::refcountable
{
protected:
    const weak< Scheduler > m_scheduler;
    const istring           m_name;
    const SchedulerType     m_type;

protected:
    IScheduler(istring name, weak< Scheduler > scheduler, SchedulerType type);
    virtual ~IScheduler();

public:
    virtual void run(weak< const Task::KernelTask > task) = 0;

    static weak< IScheduler > findScheduler(SchedulerType preferredType);
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/task/kerneltask.hh>

/**************************************************************************************************/
#endif
