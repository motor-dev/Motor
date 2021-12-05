/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_SUBWORLD_META_HH_
#define MOTOR_WORLD_SUBWORLD_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/resource/description.meta.hh>

namespace Motor { namespace World {

class motor_api(WORLD) SubWorld : public Resource::Description
{
published:
    SubWorld();
    ~SubWorld();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
