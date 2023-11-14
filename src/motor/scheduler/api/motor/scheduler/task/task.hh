/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_TASK_TASK_HH
#define MOTOR_SCHEDULER_TASK_TASK_HH

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/iexecutor.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace Task {

template < typename Executor >
class Task : public ITask
{
public:
    scoped< Executor > const executor;

public:
    /* todo: perfect forwarding of arguments to executor */
    Task(istring name, knl::color32 color, scoped< Executor >&& executor,
         Scheduler::Affinity affinity = Scheduler::WorkerThread);
    void schedule(weak< Scheduler > sc) const override;
};

}}  // namespace Motor::Task

#include <motor/scheduler/task/task.inl>

#endif
