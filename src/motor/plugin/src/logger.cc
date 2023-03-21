/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > plugin()
{
    static weak< Logger > result = system()->getChild("plugin");
    return result;
}

}}  // namespace Motor::Log
