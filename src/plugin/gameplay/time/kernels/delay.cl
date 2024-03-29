#include <motor/kernel/input/segments.hh>
#include <motor/world/update/context.hh>
#include <delay.meta.hh>

namespace Motor { namespace Gameplay {

__kernel void delay(u32 index, u32 total, knl::segments< Delay > inout)
{
    knl::segments< Delay >::iterator first = inout.begin() + (index * inout.size() / total);
    knl::segments< Delay >::iterator last = inout.begin() + ((index + 1) * inout.size() / total);
    while(first != last)
    {
        first++;
    }
}

}}  // namespace Motor::Gameplay
