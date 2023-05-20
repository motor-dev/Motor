/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > meta()
{
    static weak< Logger > result = motor()->getChild(istring("meta"));
    return result;
}

}}  // namespace Motor::Log
