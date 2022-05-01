/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASKITEM_HH_
#define MOTOR_SCHEDULER_TASKITEM_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Task {

class ITask;
class TaskScheduler;

class TaskItem
{
    friend class TaskScheduler;

private:
    weak< const ITask >     m_owner;
    weak< const IExecutor > m_executor;
    i_u32                   m_started;
    i_u32                   m_finished;
    const u32               m_total;

public:
    TaskItem(weak< const ITask > owner, weak< const IExecutor > executor, u32 totalCount);
    ~TaskItem();

private:
    TaskItem(const TaskItem& other);
    TaskItem& operator=(const TaskItem& other);
};

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
