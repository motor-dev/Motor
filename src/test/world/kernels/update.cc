#include <motor/kernel/input/segments.hh>
#include <component.meta.hh>

using namespace Motor::Test::World;

__kernel void update(u32 index, u32 total, knl::segments< Component > inout)
{
    knl::segments< Component >::iterator first = inout.begin() + (index * inout.size() / total);
    knl::segments< Component >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    for(knl::segments< Component >::iterator it = first; it != last; ++it)
    {
    }
}
