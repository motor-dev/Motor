/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > world()
{
    static weak< Logger > result = motor()->getChild("world");
    return result;
}

}}  // namespace Motor::Log
