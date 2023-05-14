/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > graphics()
{
    static weak< Logger > result = motor()->getChild(istring("graphics"));
    return result;
}

weak< Logger > shader()
{
    static weak< Logger > result = graphics()->getChild(istring("shader"));
    return result;
}

}}  // namespace Motor::Log
