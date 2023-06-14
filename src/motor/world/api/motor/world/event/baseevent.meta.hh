/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_EVENT_BASEEVENT_META_HH
#define MOTOR_WORLD_EVENT_BASEEVENT_META_HH

#include <motor/world/stdafx.h>
#include <motor/world/event/context.meta.hh>

namespace Motor { namespace World {

struct motor_api(WORLD) BaseEvent
{
private:
    const u32 m_eventIndex;

protected:
    BaseEvent();

    void raise(void* parameters);
};

}}  // namespace Motor::World

#endif
