/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASKITEM_INL_
#define MOTOR_SCHEDULER_TASKITEM_INL_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace Task {

template < typename Range, typename Body >
TaskItem< Range, Body >::TaskItem(weak< Task< Body > > owner, const Range& r, u32 index, u32 total)
    : ITaskItem(owner)
    , m_range(r.part(index, total))
    , m_body(owner->body)
{
}

template < typename Range, typename Body >
void TaskItem< Range, Body >::run(weak< Scheduler > sc)
{
    weak< Task< Body > > owner = motor_checked_cast< Task< Body > >(m_owner);
    m_body(m_range);
    if(++owner->m_taskCompleted == owner->m_taskCount)
    {
        owner->completed(sc);
    }
    this->release< TaskItem< Range, Body > >(sc);
}

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
