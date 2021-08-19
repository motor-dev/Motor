/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_RANGE_ONESTEP_INL_
#define MOTOR_SCHEDULER_RANGE_ONESTEP_INL_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/range/onestep.hh>

namespace Motor { namespace Task {

inline range_onestep::range_onestep()
{
}

inline range_onestep::~range_onestep()
{
}

inline size_t range_onestep::size() const
{
    return 1;
}

inline bool range_onestep::atomic() const
{
    return true;
}

inline u32 range_onestep::partCount(u32 /*workerCount*/) const
{
    return 1;
}

inline range_onestep range_onestep::part(u32 index, u32 total) const
{
    motor_assert(index == 0, "onestep index can only be 0");
    motor_assert(total == 1, "onestep total can only be 1");
    motor_forceuse(index);
    motor_forceuse(total);
    return *this;
}

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
