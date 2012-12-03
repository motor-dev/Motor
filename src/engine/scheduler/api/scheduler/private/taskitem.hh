/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_SCHEDULER_TASKITEM_HH_
#define BE_SCHEDULER_TASKITEM_HH_
/*****************************************************************************/
#include    <scheduler/scheduler.hh>

namespace BugEngine { namespace Task
{

class ITask;
template< typename BODY > class Task;
class TaskScheduler;

class be_api(SCHEDULER) ITaskItem : public minitl::istack<ITaskItem>::node
{
    friend class TaskScheduler;
protected:
    weak<const ITask>   m_owner;
    u32                 m_splitCount;
public:
    virtual void            run(weak<Scheduler> sc) = 0;
    virtual ITaskItem*      split(weak<Scheduler> sc) = 0;
    virtual bool            atomic() const = 0;
public:
    explicit ITaskItem(weak<const ITask> owner);
    ITaskItem(ITaskItem& cpy);
    virtual ~ITaskItem();
};

template< typename Range, typename Body >
class TaskItem : public ITaskItem
{
private:
    Range       m_range;
    const Body& m_body;
public:
    TaskItem(weak< const Task<Body> > owner, const Range& r, const Body& b);
    TaskItem(TaskItem& split);

    virtual void            run(weak<Scheduler> sc) override;
    virtual ITaskItem*      split(weak<Scheduler> sc) override;
    virtual bool            atomic() const override;
};

}}

#include    <scheduler/private/taskitem.inl>

/*****************************************************************************/
#endif