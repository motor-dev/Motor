/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>

namespace Motor { namespace Arena {

minitl::Allocator& meta()
{
    return general();
}
minitl::Allocator& script()
{
    return general();
}

}}  // namespace Motor::Arena
