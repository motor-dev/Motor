/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>

namespace Motor { namespace Arena {

minitl::allocator& resource()
{
    return general();
}

}}  // namespace Motor::Arena
