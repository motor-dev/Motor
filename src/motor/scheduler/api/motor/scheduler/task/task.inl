/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASL_TASK_INL_
#define MOTOR_SCHEDULER_TASL_TASK_INL_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Task {

template < typename Executor >
Task< Executor >::Task(istring name, color32 color, ref< Executor > executor,
                       Scheduler::Affinity affinity)
    : ITask(name, color, affinity)
    , executor(executor)
{
}

template < typename Executor >
void Task< Executor >::schedule(weak< Scheduler > sc) const
{
    u32 splitCount = executor->partCount(sc->workerCount());
    sc->queueTask(this, executor, splitCount);
}

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
