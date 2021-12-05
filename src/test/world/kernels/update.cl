#include <motor/kernel/input/segments.hh>
#include <component.meta.hh>

using namespace Motor::Test::World;

__kernel void update(u32 index, u32 total, Kernel::segments< Component > inout)
{
    Kernel::segments< Component >::iterator first = inout.begin() + (index * inout.size() / total);
    Kernel::segments< Component >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    for(Kernel::segments< Component >::iterator it = first; it != last; ++it)
    {
    }
}
