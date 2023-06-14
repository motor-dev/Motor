/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GAMEPLAY_TIME_DELAY_META_HH
#define MOTOR_PLUGIN_GAMEPLAY_TIME_DELAY_META_HH

#include <stdafx.h>
#include <motor/world/component/component.meta.hh>
#include <motor/world/event/event.hh>

namespace Motor { namespace Gameplay {

class DelayKernel;

motor_tag(World::LogicComponent(motor_class< Motor::Gameplay::DelayKernel >())) struct Delay
{
    float delay;

    // void begin();
    // void reset(float newDelay);

    // static World::Event<> startAction;
};

}}  // namespace Motor::Gameplay

#endif
