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

public:
    MethodCaller& operator=(const MethodCaller& other) = delete;

public:
    explicit MethodCaller(Ptr< Owner > owner) : m_owner(owner)
    {
    }
    ~MethodCaller() override = default;
    MethodCaller(const MethodCaller& other) : m_owner(other.m_owner)
    {
    }

    u32 partCount(u32 threadCount) const
    {
        motor_forceuse(threadCount);
        return 1;
    }

    void run(u32 partIndex, u32 partCount) const override
    {
        motor_assert_format(partIndex == 0, "MethodCaller called with invalid part index {0}",
                            partIndex);
        motor_assert_format(partCount == 1, "MethodCaller called with invalid part count {0}",
                            partCount);
        (m_owner.operator->()->*Method)();
    }
};

template < void (*Procedure)() >
struct ProcedureCaller : public IExecutor
{
public:
    ProcedureCaller& operator=(const ProcedureCaller& other) = delete;

public:
    ProcedureCaller()           = default;
    ~ProcedureCaller() override = default;
    ProcedureCaller(const ProcedureCaller& other)
    {
        motor_forceuse(other);
    }

    u32 partCount(u32 threadCount) const
    {
        motor_forceuse(threadCount);
        return 1;
    }

    void run(u32 partIndex, u32 partCount) const override
    {
        motor_assert_format(partIndex == 0, "MethodCaller called with invalid part index {0}",
                            partIndex);
        motor_assert_format(partCount == 1, "MethodCaller called with invalid part count {0}",
                            partCount);
        (*Procedure)();
    }
};

}}  // namespace Motor::Task
