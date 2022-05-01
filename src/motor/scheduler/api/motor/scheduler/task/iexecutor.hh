/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_TASK_IEXECUTOR_HH_
#define MOTOR_SCHEDULER_TASK_IEXECUTOR_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Task {

class motor_api(SCHEDULER) IExecutor : public minitl::refcountable
{
    MOTOR_NOCOPY(IExecutor);

protected:
    IExecutor()
    {
    }

public:
    virtual void run(u32 partIndex, u32 partTotal) const = 0;
};

}}  // namespace Motor::Task

/**************************************************************************************************/
#endif
