/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_TASK_ITASK_HH
#define MOTOR_SCHEDULER_TASK_ITASK_HH

#include <motor/scheduler/stdafx.h>
#include <motor/core/threads/criticalsection.hh>
#include <motor/kernel/colors.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Task {

class motor_api(SCHEDULER) ITask : public minitl::pointer
{
public:
    class CallbackConnection;
    class motor_api(SCHEDULER) ICallback : public minitl::pointer
    {
    protected:
        ICallback();

    public:
        enum CallbackStatus
        {
            Pending,
            Completed
        };

        ~ICallback() override;

        virtual void onCompleted(weak< Scheduler > scheduler, weak< const ITask > task) = 0;
        virtual void onConnected(weak< ITask > to, CallbackStatus)                      = 0;
        virtual bool onDisconnected(weak< ITask > from)                                 = 0;
    };
    friend class CallbackConnection;

private:
    class ChainCallback : public ICallback
    {
    private:
        weak< ITask > const             m_starts;
        minitl::vector< weak< ITask > > m_startedBy;
        i_u32                           m_completed;

    public:
        explicit ChainCallback(const weak< ITask >& task);
        ~ChainCallback() override;

        void onCompleted(weak< Scheduler > scheduler, weak< const ITask > task) override;
        void onConnected(weak< ITask > to, CallbackStatus status) override;
        bool onDisconnected(weak< ITask > from) override;

    private:
        ChainCallback(const ChainCallback& other);
        ChainCallback& operator=(const ChainCallback& other);
    };

public:
    const istring             name;
    const knl::color32        color;
    const Scheduler::Affinity affinity;

private:
    minitl::vector< weak< ICallback > > m_callbacks;
    ref< ICallback >                    m_start;
    CriticalSection                     m_cs;

private:
    void addCallback(const weak< ICallback >& callback, ICallback::CallbackStatus status);
    bool removeCallback(const weak< ICallback >& callback);

public:
    ~ITask() override;

    virtual void schedule(weak< Scheduler > scheduler) const = 0;
    void         completed(const weak< Scheduler >& scheduler) const;

    weak< ICallback > startCallback();

protected:
    ITask(istring name, knl::color32 color, Scheduler::Affinity affinity);
};

class motor_api(SCHEDULER) ITask::CallbackConnection
{
private:
    weak< ITask >            m_task;
    weak< ITask::ICallback > m_callback;

public:
    CallbackConnection();
    CallbackConnection(const weak< ITask >& task, const weak< ICallback >& callback,
                       ICallback::CallbackStatus status = ICallback::Pending);
    CallbackConnection(const CallbackConnection& other);
    CallbackConnection& operator=(const CallbackConnection& other);
    ~CallbackConnection();

    void clear();
};

}}  // namespace Motor::Task

#endif
