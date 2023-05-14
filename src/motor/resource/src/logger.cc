/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > resource()
{
    static weak< Logger > result = system()->getChild(istring("resource"));
    return result;
}

}}  // namespace Motor::Log
