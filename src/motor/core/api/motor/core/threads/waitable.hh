/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_THREADS_WAITABLE_HH
#define MOTOR_CORE_THREADS_WAITABLE_HH

#include <motor/core/stdafx.h>

namespace Motor { namespace Threads {

class motor_api(CORE) Waitable
{
public:
    Waitable()          = default;
    virtual ~Waitable() = default;

    enum WaitResult
    {
        Finished,
        Abandoned
    };

protected:
    virtual WaitResult wait() = 0;
};

}}  // namespace Motor::Threads

#endif
