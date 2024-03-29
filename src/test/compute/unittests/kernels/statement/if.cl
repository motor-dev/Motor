#include <motor/kernel/input/segments.hh>
#include <component.meta.hh>

using namespace Motor::Test::Compute::UnitTests;

__kernel void if_then(u32 index, u32 total, knl::segments< ComponentInt > inout)
{
    knl::segments< ComponentInt >::iterator first
        = inout.begin() + (index * inout.size() / total);
    knl::segments< ComponentInt >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    for(knl::segments< ComponentInt >::iterator it = first; it != last; ++it)
    {
        if(it->value < 0) it->value = -it->value;
    }
}

__kernel void if_then_else(u32 index, u32 total, knl::segments< ComponentInt > inout)
{
    knl::segments< ComponentInt >::iterator first
        = inout.begin() + (index * inout.size() / total);
    knl::segments< ComponentInt >::iterator last
        = inout.begin() + ((index + 1) * inout.size() / total);
    for(knl::segments< ComponentInt >::iterator it = first; it != last; ++it)
    {
        if(it->value % 2 == 0)
            it->value = -it->value;
        else
            it->value = 0;
    }
}
