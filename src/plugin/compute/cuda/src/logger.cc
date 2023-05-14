/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > cuda()
{
    static weak< Logger > result = compute()->getChild(istring("cuda"));
    return result;
}

}}  // namespace Motor::Log
