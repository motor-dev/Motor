/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

namespace Motor { namespace Log {

weak< Logger > lua()
{
    static weak< Logger > result = motor()->getChild(istring("lua"));
    return result;
}

}}  // namespace Motor::Log
