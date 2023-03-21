/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

namespace Motor { namespace Log {

weak< Logger > opencl_gl()
{
    static weak< Logger > result = compute()->getChild("opencl_gl");
    return result;
}

}}  // namespace Motor::Log
