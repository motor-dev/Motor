/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Arena {

minitl::allocator& task()
{
    return general();
}

}}  // namespace Motor::Arena
