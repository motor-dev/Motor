/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > cpu()
{
    static weak< Logger > result = compute()->getChild(istring("cpu"));
    return result;
}

}}  // namespace Motor::Log
