/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GAMEPLAY_TIMER_DELA_META_HH_
#define MOTOR_GAMEPLAY_TIMER_DELA_META_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/world/component/component.meta.hh>
#include <motor/world/event/event.hh>

namespace Motor { namespace Gameplay {

class DelayKernel;

motor_tag(World::LogicComponent(motor_class< Motor::Gameplay::DelayKernel >())) motor_pod Delay
{
    float delay;

    void begin();
    void reset(float newDelay);

    static World::Event<> startAction;
};

}}  // namespace Motor::Gameplay

/**************************************************************************************************/
#endif
