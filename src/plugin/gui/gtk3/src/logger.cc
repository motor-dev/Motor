/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

namespace Motor { namespace Log {

weak< Logger > gtk()
{
    static weak< Logger > result = motor()->getChild(istring("gtk"));
    return result;
}

}}  // namespace Motor::Log
