/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/event/baseevent.meta.hh>

namespace Motor { namespace World {

static i_u32 s_eventIndex;

BaseEvent::BaseEvent() : m_eventIndex(s_eventIndex++)
{
}

}}  // namespace Motor::World
