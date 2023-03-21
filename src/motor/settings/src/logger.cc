/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/settings/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > settings()
{
    static weak< Logger > result = system()->getChild("settings");
    return result;
}

}}  // namespace Motor::Log
