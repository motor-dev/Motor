/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > graphics()
{
    static weak< Logger > result = motor()->getChild("graphics");
    return result;
}

weak< Logger > shader()
{
    static weak< Logger > result = graphics()->getChild("shader");
    return result;
}

}}  // namespace Motor::Log
