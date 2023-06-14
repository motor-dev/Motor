/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_COMPONENT_COMPONENT_META_HH
#define MOTOR_WORLD_COMPONENT_COMPONENT_META_HH

#include <motor/world/stdafx.h>

#ifndef MOTOR_COMPUTE

namespace Motor { namespace World {

struct motor_api(WORLD) Component
{
    Component();
};

struct motor_api(WORLD) LogicComponent
{
    raw< const Meta::Class > const kernelClass;

    explicit LogicComponent(raw< const Meta::Class > kernelClass
                            = raw< const Meta::Class >::null());
};

}}  // namespace Motor::World

#endif

#endif
