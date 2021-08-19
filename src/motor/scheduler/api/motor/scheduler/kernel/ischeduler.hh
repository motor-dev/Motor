/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_ISCHEDULER_HH_
#define MOTOR_SCHEDULER_KERNEL_ISCHEDULER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/kernel.script.hh>
#include <motor/scheduler/task/kerneltask.hh>

namespace Motor {
class Scheduler;
}

namespace Motor { namespace KernelScheduler {

class IMemoryHost;

class motor_api(SCHEDULER) IKernelTaskItem
{
    friend class Motor::Scheduler;

protected:
    weak< Task::KernelTask >                     m_owner;
    weak< const Kernel >                         m_kernel;
    minitl::array< weak< const IMemoryBuffer > > m_parameters;

protected:
    IKernelTaskItem(weak< Task::KernelTask > ownerTask, weak< const Kernel > kernel,
                    u32 parameterCount);
    virtual ~IKernelTaskItem();

public:
    weak< Task::KernelTask > owner() const
    {
        return m_owner;
    }
    weak< const Kernel > kernel() const
    {
        return m_kernel;
    }
    const minitl::array< weak< const IMemoryBuffer > >& parameters() const
    {
        return m_parameters;
    }
};

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
    virtual IKernelTaskItem* allocateItem(weak< Task::KernelTask > task,
                                          weak< const Kernel > kernel, u32 parametercount)
        = 0;
    virtual void                run(IKernelTaskItem * item) = 0;
    virtual weak< IMemoryHost > memoryHost() const          = 0;

    static weak< IScheduler > findScheduler(SchedulerType preferredType);
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
