/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASK_TASK_HH_
#define MOTOR_SCHEDULER_TASK_TASK_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/private/taskitem.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace Task {

template < typename Body >
class Task : public ITask
{
    template < class B, class R >
    friend class TaskItem;
    MOTOR_NOCOPY(Task);

public:
    Body body;

private:
    i_u32 m_taskCount;
    i_u32 m_taskCompleted;

public:
    Task(istring name, color32 color, const Body& body,
         Scheduler::Priority priority = Scheduler::Default,
         Scheduler::Affinity affinity = Scheduler::WorkerThread);
    virtual void schedule(weak< Scheduler > sc) override;
};

}}  // namespace Motor::Task

#include <motor/scheduler/task/task.inl>

/**************************************************************************************************/
#endif
