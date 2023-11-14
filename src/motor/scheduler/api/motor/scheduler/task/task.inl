/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_TASK_TASK_INL
#define MOTOR_SCHEDULER_TASK_TASK_INL
#pragma once

#include <motor/scheduler/task/task.hh>

#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Task {

template < typename Executor >
Task< Executor >::Task(istring name, knl::color32 color, scoped< Executor >&& executor,
                       Scheduler::Affinity affinity)
    : ITask(name, color, affinity)
    , executor(minitl::move(executor))
{
}

template < typename Executor >
void Task< Executor >::schedule(weak< Scheduler > sc) const
{
    u32 splitCount = executor->partCount(sc->workerCount());
    sc->queueTask(this, executor, splitCount);
}

}}  // namespace Motor::Task

#endif
