/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_ENTITY_SCRIPT_HH_
#define MOTOR_WORLD_ENTITY_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

namespace Motor { namespace World {

struct motor_api(WORLD) Entity
{
    const u32 id;

    bool operator==(const Entity other) const
    {
        return id == other.id;
    }
    bool operator!=(const Entity other) const
    {
        return id != other.id;
    }
    bool operator<(const Entity other) const
    {
        return id < other.id;
    }
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
