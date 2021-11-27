/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_RESOURCE_HANDLE_META_HH_
#define MOTOR_WORLD_RESOURCE_HANDLE_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace World {

motor_pod ResourceHandle
{
    void* const resource;
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
