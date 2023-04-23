/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace Task {

class motor_api(SCHEDULER) TaskGroup : public ITask
{
public:
    class TaskStartConnection;
    friend class TaskStartConnection;
    class TaskEndConnection;
    friend class TaskEndConnection;

private:
    class Callback : public ICallback
    {
    private:
        weak< TaskGroup > m_owner;
        i_u32             m_completed;

    public:
        explicit Callback(const weak< TaskGroup >& owner);
        ~Callback() override;

        void onCompleted(weak< Scheduler > scheduler, weak< const ITask > task) override;
        void onConnected(weak< ITask > to, CallbackStatus status) override;
        bool onDisconnected(weak< ITask > to) override;
    };
    friend class Callback;

public:
    TaskGroup(istring name, knl::color32 color);
    ~TaskGroup() override;

public:  // ITask
    void schedule(weak< Scheduler > scheduler) const override;

public:
    void addStartTask(const weak< ITask >& task);
    bool removeStartTask(weak< ITask > task);

private:
    minitl::vector< weak< ITask > > m_startTasks;
    i_u32                           m_endTaskCount;
    ref< Callback >                 m_completionCallback;
};

class motor_api(SCHEDULER) TaskGroup::TaskStartConnection
{
private:
    weak< TaskGroup > m_group;
    weak< ITask >     m_task;

public:
    TaskStartConnection();
    TaskStartConnection(const weak< TaskGroup >& group, const weak< ITask >& task);
    TaskStartConnection(const TaskStartConnection& other);
    TaskStartConnection& operator=(const TaskStartConnection& other);
    ~TaskStartConnection();
};

class motor_api(SCHEDULER) TaskGroup::TaskEndConnection
{
private:
    weak< TaskGroup >  m_group;
    weak< ITask >      m_task;
    CallbackConnection m_callback;

public:
    TaskEndConnection();
    TaskEndConnection(const weak< TaskGroup >& group, const weak< ITask >& task);
    TaskEndConnection(const TaskEndConnection& other);
    TaskEndConnection& operator=(const TaskEndConnection& other);
    ~TaskEndConnection();
};

}}  // namespace Motor::Task
