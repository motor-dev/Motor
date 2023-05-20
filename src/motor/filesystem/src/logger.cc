/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > fs()
{
    static weak< Logger > result = system()->getChild(istring("fs"));
    return result;
}

}}  // namespace Motor::Log
