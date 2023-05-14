/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > package()
{
    static weak< Logger > result = resource()->getChild(istring("package"));
    return result;
}

}}  // namespace Motor::Log
