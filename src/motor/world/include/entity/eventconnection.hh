/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_ENTITY_EVENTCONNECTION_HH_
#define MOTOR_WORLD_ENTITY_EVENTCONNECTION_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

namespace Motor { namespace World {

struct motor_api(WORLD) CommandConnection
{
    const u32 entityIndex;
    const u16 componentIndex;
    const u16 commandIndex;
};

struct motor_api(WORLD) CommandConnectionList
{
    CommandConnectionList*  previous;
    CommandConnectionList*  next;
    const u32               subworldIndex;
    const u32               connectionCount;
    const CommandConnection connections[1];
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
