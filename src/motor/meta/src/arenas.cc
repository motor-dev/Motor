/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>

namespace Motor { namespace Arena {

minitl::allocator& meta()
{
    return general();
}
minitl::allocator& script()
{
    return general();
}

}}  // namespace Motor::Arena
