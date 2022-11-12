#include <motor/kernel/input/segments.hh>
#include <component.meta.hh>

using namespace Motor::Test::Compute::UnitTests;

__kernel void for_loop(u32 index, u32 total, knl::segments< ComponentInt > inout)
{
    knl::segments< ComponentInt >::iterator first
        = inout.begin() + (index * inout.size() / total);
    knl::segments< ComponentInt >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    for(knl::segments< ComponentInt >::iterator it = first; it != last; ++it)
    {
        it->value *= 2;
    }
}

__kernel void while_loop(u32 index, u32 total, knl::segments< ComponentInt > inout)
{
    knl::segments< ComponentInt >::iterator first
        = inout.begin() + (index * inout.size() / total);
    knl::segments< ComponentInt >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    while(first != last)
    {
        (first++)->value *= 3;
    }
}
