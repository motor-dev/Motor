/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > windowing()
{
    static weak< Logger > result = graphics()->getChild(istring("windowing"));
    return result;
}

}}  // namespace Motor::Log
