/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > python()
{
    static weak< Logger > result = motor()->getChild(istring("python"));
    return result;
}

}}  // namespace Motor::Log
