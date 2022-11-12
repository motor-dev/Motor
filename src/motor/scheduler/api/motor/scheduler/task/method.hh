/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace Task {

template < typename Owner, void (Owner::*Method)(),
           template < typename > class Ptr = ::minitl::weak >
struct MethodCaller : public IExecutor
{
private:
    Ptr< Owner > const m_owner;

private:
    MethodCaller& operator=(const MethodCaller& other);

public:
    MethodCaller(Ptr< Owner > owner) : m_owner(owner)
    {
    }
    ~MethodCaller()
    {
    }
    MethodCaller(const MethodCaller& other) : m_owner(other.m_owner)
    {
    }

    u32 partCount(u32 threadCount) const
    {
        motor_forceuse(threadCount);
        return 1;
    }

    virtual void run(u32 partIndex, u32 partCount) const override
    {
        motor_assert(partIndex == 0, "MethodCaller called with invalid part index %d" | partIndex);
        motor_assert(partCount == 1, "MethodCaller called with invalid part count %d" | partCount);
        (m_owner.operator->()->*Method)();
    }
};

template < void (*Procedure)() >
struct ProcedureCaller : public IExecutor
{
private:
    ProcedureCaller& operator=(const ProcedureCaller& other);

public:
    ProcedureCaller()
    {
    }
    ~ProcedureCaller()
    {
    }
    ProcedureCaller(const ProcedureCaller& other)
    {
        motor_forceuse(other);
    }

    u32 partCount(u32 threadCount) const
    {
        motor_forceuse(threadCount);
        return 1;
    }

    virtual void run(u32 partIndex, u32 partCount) const override
    {
        motor_assert(partIndex == 0, "MethodCaller called with invalid part index %d" | partIndex);
        motor_assert(partCount == 1, "MethodCaller called with invalid part count %d" | partCount);
        (*Procedure)();
    }
};

}}  // namespace Motor::Task
