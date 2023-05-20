/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > gl()
{
    static weak< Logger > result = graphics()->getChild(istring("gl"));
    return result;
}

}}  // namespace Motor::Log
