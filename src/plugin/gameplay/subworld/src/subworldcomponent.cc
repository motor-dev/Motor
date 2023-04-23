/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <subworldcomponent.meta.hh>

namespace Motor { namespace World {

void SubWorldComponent::load(const EntityContext& owner, EventContext& context)
{
    motor_forceuse(this);
    motor_forceuse(owner);
    motor_forceuse(context);
}
void SubWorldComponent::unload(const EntityContext& owner, EventContext& context)
{
    motor_forceuse(this);
    motor_forceuse(owner);
    motor_forceuse(context);
}
void SubWorldComponent::spawn(const EntityContext& owner, EventContext& context)
{
    motor_forceuse(this);
    motor_forceuse(owner);
    motor_forceuse(context);
}
void SubWorldComponent::despawn(const EntityContext& owner, EventContext& context, u32 instance)
{
    motor_forceuse(this);
    motor_forceuse(owner);
    motor_forceuse(context);
    motor_forceuse(instance);
}

Event<>      SubWorldComponent::loaded    = {0};
Event<>      SubWorldComponent::unloaded  = {1};
Event< u32 > SubWorldComponent::spawned   = {2};
Event< u32 > SubWorldComponent::despawned = {3};

}}  // namespace Motor::World
