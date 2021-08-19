/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/allocators/general.hh>

namespace Motor { namespace Arena {

minitl::Allocator& general()
{
    static GeneralAllocator s_allocator;
    return s_allocator;
}

minitl::Allocator& temporary()
{
    return general();
}

minitl::Allocator& stack()
{
    return general();
}

minitl::Allocator& debug()
{
    return general();
}

}}  // namespace Motor::Arena
