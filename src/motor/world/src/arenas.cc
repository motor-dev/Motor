/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>

namespace Motor { namespace Arena {

minitl::allocator& game()
{
    return general();
}

}}  // namespace Motor::Arena
