/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>

namespace Motor { namespace Log {

weak< Logger > opencl()
{
    static weak< Logger > result = compute()->getChild("opencl");
    return result;
}

}}  // namespace Motor::Log
