/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_RANGE_ONESTEP_HH_
#define MOTOR_SCHEDULER_RANGE_ONESTEP_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Task {

class range_onestep
{
public:
    range_onestep();
    ~range_onestep();

    inline size_t        size() const;
    inline u32           partCount(u32 workerCount) const;
    inline range_onestep part(u32 index, u32 total) const;
    inline bool          atomic() const;
};

}}  // namespace Motor::Task

#include <motor/scheduler/range/onestep.inl>

/**************************************************************************************************/
#endif
