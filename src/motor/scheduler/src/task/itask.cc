/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace Task {

ITask::ITask(istring name, knl::color32 color, Scheduler::Affinity affinity)
    : name(name)
    , color(color)
    , affinity(affinity)
    , m_callbacks(Arena::task())
    , m_start(scoped< ChainCallback >::create(Arena::task(), this))
{
}

ITask::~ITask()
{
    ScopedCriticalSection scope(m_cs);
    for(auto& m_callback: m_callbacks)
    {
        bool result = m_callback->onDisconnected(this);
        motor_forceuse(result);
        motor_assert(result, "unable to disconnect callback");
    }
}

void ITask::completed(const weak< Scheduler >& sc) const
{
    ScopedCriticalSection scope(m_cs);
    for(const auto& m_callback: m_callbacks)
    {
        m_callback->onCompleted(sc, this);
    }
}

void ITask::addCallback(const weak< ICallback >& callback, ICallback::CallbackStatus status)
{
    ScopedCriticalSection scope(m_cs);
    m_callbacks.push_back(callback);
    callback->onConnected(this, status);
}

bool ITask::removeCallback(const weak< ICallback >& callback)
{
    ScopedCriticalSection scope(m_cs);
    for(minitl::vector< weak< ICallback > >::iterator it = m_callbacks.begin();
        it != m_callbacks.end(); ++it)
    {
        if(*it == callback)
        {
            bool result = (*it)->onDisconnected(this);
            m_callbacks.erase(it);
            motor_forceuse(result);
            motor_assert(result, "unable to disconnect callback");
            return true;
        }
    }
    return false;
}

weak< ITask::ICallback > ITask::startCallback()
{
    return m_start;
}

/*----------------------------------------------------------------------------*/

ITask::ICallback::ICallback() = default;

ITask::ICallback::~ICallback() = default;

/*----------------------------------------------------------------------------*/

ITask::ChainCallback::ChainCallback(const weak< ITask >& task)
    : ICallback()
    , m_starts(task)
    , m_startedBy(Arena::task())
    , m_completed(i_u32::create(0))
{
}

ITask::ChainCallback::~ChainCallback()
{
    while(!m_startedBy.empty())
    {
        bool result = m_startedBy.back()->removeCallback(this);
        motor_forceuse(result);
        motor_assert_format(result, "unable to disconnect from task {0}",
                            m_startedBy.back()->name.c_str());
    }
}

void ITask::ChainCallback::onCompleted(weak< Scheduler > scheduler, weak< const ITask > /*task*/)
{
    if(++m_completed == m_startedBy.size())
    {
        m_completed.set(0);
        m_starts->schedule(scheduler);
    }
}

void ITask::ChainCallback::onConnected(weak< ITask > to, CallbackStatus status)
{
    m_startedBy.push_back(to);
    if(status == Completed)
    {
        m_completed++;
    }
}

bool ITask::ChainCallback::onDisconnected(weak< ITask > from)
{
    for(minitl::vector< weak< ITask > >::iterator it = m_startedBy.begin(); it != m_startedBy.end();
        ++it)
    {
        if((*it) == from)
        {
            m_startedBy.erase(it);
            return true;
        }
    }
    return false;
}

/*----------------------------------------------------------------------------*/

ITask::CallbackConnection::CallbackConnection() : m_task(nullptr), m_callback(nullptr)
{
}

ITask::CallbackConnection::CallbackConnection(const weak< ITask >&      task,
                                              const weak< ICallback >&  callback,
                                              ICallback::CallbackStatus status)
    : m_task(task)
    , m_callback(callback)
{
    if(m_task)
    {
        m_task->addCallback(m_callback, status);
    }
}

ITask::CallbackConnection::CallbackConnection(const CallbackConnection& other)
    : m_task(other.m_task)
    , m_callback(other.m_callback)
{
    if(m_task)
    {
        m_task->addCallback(m_callback, ICallback::Pending);
    }
}

ITask::CallbackConnection& ITask::CallbackConnection::operator=(const CallbackConnection& other)
{
    if(m_task)
    {
        bool result = m_task->removeCallback(m_callback);
        motor_forceuse(result);
        motor_assert_format(result, "could not disconnect callback from task {0}", m_task->name);
    }
    m_task     = other.m_task;
    m_callback = other.m_callback;
    if(m_task)
    {
        m_task->addCallback(m_callback, ICallback::Pending);
    }
    return *this;
}

ITask::CallbackConnection::~CallbackConnection()
{
    if(m_task)
    {
        bool result = m_task->removeCallback(m_callback);
        motor_forceuse(result);
        motor_assert_format(result, "could not disconnect callback from task {0}", m_task->name);
    }
}

void ITask::CallbackConnection::clear()
{
    if(m_task)
    {
        bool result = m_task->removeCallback(m_callback);
        motor_forceuse(result);
        motor_assert_format(result, "could not disconnect callback from task {0}", m_task->name);
    }
    m_task.clear();
    m_callback.clear();
}

}}  // namespace Motor::Task
