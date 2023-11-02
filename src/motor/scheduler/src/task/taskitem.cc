/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/task.hh>
#include <taskitem.hh>

namespace Motor { namespace Task {

TaskItem::TaskItem(const weak< const ITask >& owner, const weak< const IExecutor >& executor,
                   u32 totalCount)
    : m_owner(owner)
    , m_executor(executor)
    , m_started(i_u32::create(0))
    , m_finished(i_u32::create(0))
    , m_total(totalCount)
{
}

TaskItem::~TaskItem() = default;

}}  // namespace Motor::Task
