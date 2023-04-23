/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
