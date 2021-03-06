/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace KernelScheduler {

static minitl::vector< weak< IScheduler > > s_schedulers(Arena::task());

IScheduler::IScheduler(istring name, weak< Scheduler > scheduler, SchedulerType type)
    : m_scheduler(scheduler)
    , m_name(name)
    , m_type(type)
{
    s_schedulers.push_back(this);
}

IScheduler::~IScheduler()
{
    for(minitl::vector< weak< IScheduler > >::iterator it = s_schedulers.begin();
        it != s_schedulers.end(); ++it)
    {
        if(*it == this)
        {
            s_schedulers.erase(it);
            return;
        }
    }
    motor_notreached();
}

weak< IScheduler > IScheduler::findScheduler(SchedulerType preferredType)
{
    weak< IScheduler > result;
    for(minitl::vector< weak< IScheduler > >::iterator it = s_schedulers.begin();
        it != s_schedulers.end(); ++it)
    {
        if((*it)->m_type == preferredType)
        {
            return *it;
        }
        else
        {
            result = *it;
        }
    }
    return result;
}

}}  // namespace Motor::KernelScheduler
