/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SUBWORLD_SUBWORLDCOMPONENT_META_HH
#define MOTOR_PLUGIN_SUBWORLD_SUBWORLDCOMPONENT_META_HH

#include <stdafx.h>
#include <motor/world/component/component.meta.hh>
#include <motor/world/entity/context.meta.hh>
#include <motor/world/event/context.meta.hh>
#include <motor/world/event/event.meta.hh>

namespace Motor { namespace World {

struct [[motor::meta(tag = LogicComponent)]] SubWorldComponent
{
    void load(const EntityContext& owner, EventContext& context);
    void unload(const EntityContext& owner, EventContext& context);
    void spawn(const EntityContext& owner, EventContext& context);
    void despawn(const EntityContext& owner, EventContext& context, u32 instance);

    static Event<>      loaded;
    static Event<>      unloaded;
    static Event< u32 > spawned;
    static Event< u32 > despawned;
};

}}  // namespace Motor::World

#include <subworldcomponent.meta.factory.hh>
#endif
