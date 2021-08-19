/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASK_METHOD_HH_
#define MOTOR_SCHEDULER_TASK_METHOD_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/range/onestep.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace Task {

template < typename Owner, void (Owner::*Method)(),
           template < typename > class Ptr = ::minitl::weak >
struct MethodCaller
{
private:
    Ptr< Owner > const m_owner;

private:
    MethodCaller& operator=(const MethodCaller& other);

public:
    typedef range_onestep Range;
    MethodCaller(Ptr< Owner > owner) : m_owner(owner)
    {
    }
    ~MethodCaller()
    {
    }
    MethodCaller(const MethodCaller& other) : m_owner(other.m_owner)
    {
    }

    Range prepare()
    {
        return Range();
    }
    void operator()(const Range& /*r*/) const
    {
        (m_owner.operator->()->*Method)();
    }
    void operator()(Range& /*myRange*/, MethodCaller& /*with*/, Range& /*withRange*/)
    {
    }
};

template < void (*Procedure)() >
struct ProcedureCaller
{
private:
    ProcedureCaller& operator=(const ProcedureCaller& other);

public:
    typedef range_onestep Range;
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

    range_onestep prepare()
    {
        return range_onestep();
    }
    void operator()(const range_onestep& /*r*/) const
    {
        (*Procedure)();
    }
    void operator()(range_onestep& /*myRange*/, ProcedureCaller& /*with*/,
                    range_onestep& /*withRange*/)
    {
    }
};

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
