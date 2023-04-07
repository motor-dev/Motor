/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > text()
{
    static weak< Logger > result = graphics()->getChild("text");
    return result;
}

}}  // namespace Motor::Log
