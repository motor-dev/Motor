/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/private/taskitem.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace Task {

ITaskItem::ITaskItem(weak< ITask > owner) : m_owner(owner)
{
}

ITaskItem::~ITaskItem()
{
}

}}  // namespace Motor::Task
