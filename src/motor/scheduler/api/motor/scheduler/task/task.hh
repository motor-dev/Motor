/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/iexecutor.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace Task {

template < typename Executor >
class Task : public ITask
{
    MOTOR_NOCOPY(Task);

public:
    ref< Executor > const executor;

public:
    /* todo: perfect forwarding of arguments to executor */
    Task(istring name, knl::color32 color, ref< Executor > executor,
         Scheduler::Affinity affinity = Scheduler::WorkerThread);
    virtual void schedule(weak< Scheduler > sc) const override;
};

}}  // namespace Motor::Task

#include <motor/scheduler/task/task.inl>
