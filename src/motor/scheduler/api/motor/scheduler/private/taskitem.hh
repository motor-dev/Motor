/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASKITEM_HH_
#define MOTOR_SCHEDULER_TASKITEM_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Task {

class ITask;
template < typename BODY >
class Task;
class TaskScheduler;

class motor_api(SCHEDULER) ITaskItem : public minitl::istack< ITaskItem >::node
{
    friend class TaskScheduler;

protected:
    weak< ITask > m_owner;

protected:
    template < typename T >
    void release(weak< Scheduler > scheduler)
    {
        return scheduler->releaseTask< T >(minitl::motor_checked_cast< T >(this));
    }

public:
    virtual void run(weak< Scheduler > sc) = 0;

public:
    ITaskItem(weak< ITask > owner);
    virtual ~ITaskItem();

private:
    ITaskItem(const ITaskItem& other);
    ITaskItem& operator=(const ITaskItem& other);
};

template < typename Range, typename Body >
class TaskItem : public ITaskItem
{
    friend class Task< Body >;

private:
    Range       m_range;
    const Body& m_body;

public:
    virtual void run(weak< Scheduler > sc) override;

private:
    TaskItem(weak< Task< Body > > owner, const Range& r, u32 index, u32 total);

private:
    TaskItem(const TaskItem& other);
    TaskItem& operator=(const TaskItem& other);
};

}}  // namespace Motor::Task

#include <motor/scheduler/private/taskitem.inl>

/**************************************************************************************************/
#endif
