/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > scheduler()
{
    static weak< Logger > result = system()->getChild(istring("scheduler"));
    return result;
}

weak< Logger > compute()
{
    static weak< Logger > result = system()->getChild(istring("compute"));
    return result;
}

}}  // namespace Motor::Log
