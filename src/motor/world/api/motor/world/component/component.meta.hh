/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_COMPONENT_COMPONENT_META_HH_
#define MOTOR_WORLD_COMPONENT_COMPONENT_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

#define motor_pod struct

#ifndef MOTOR_COMPUTE

namespace Motor { namespace World {

struct motor_api(WORLD) Component
{
    Component();
};

struct motor_api(WORLD) LogicComponent
{
    raw< const Meta::Class > const kernelClass;

    LogicComponent(raw< const Meta::Class > kernelClass = raw< const Meta::Class >::null());
};

}}  // namespace Motor::World

#endif

/**************************************************************************************************/
#endif
