/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>

namespace Motor { namespace Arena {

minitl::allocator& filesystem()
{
    return general();
}

}}  // namespace Motor::Arena
