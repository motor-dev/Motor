/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/general.hh>

namespace Motor { namespace Arena {

minitl::allocator& general()
{
    static GeneralAllocator s_allocator;
    return s_allocator;
}

minitl::allocator& temporary()
{
    return general();
}

minitl::allocator& stack()
{
    return general();
}

minitl::allocator& debug()
{
    return general();
}

}}  // namespace Motor::Arena
