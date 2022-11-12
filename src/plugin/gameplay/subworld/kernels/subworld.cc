#include <motor/kernel/input/segments.hh>
#include <motor/world/update/context.hh>
#include <subworldcomponent.meta.hh>

namespace Motor { namespace World {

__kernel void update(u32 index, u32 total,
                     knl::segments< Motor::World::SubWorldComponent > subworlds)
{
    using namespace Motor;
    using namespace Motor::World;
    knl::segments< SubWorldComponent >::iterator first
        = subworlds.begin() + (index * subworlds.size() / total);
    knl::segments< SubWorldComponent >::iterator last
        = subworlds.begin() + ((index + 1) * subworlds.size() / total);
    while(first != last)
    {
        first++;
    }
}

}}