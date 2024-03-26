/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_EVENT_EVENT_META_HH
#define MOTOR_WORLD_EVENT_EVENT_META_HH

#include <motor/world/stdafx.h>

namespace Motor { namespace World {

template < typename T1 = void, typename T2 = void, typename T3 = void, typename T4 = void >
struct Event
{
public:
    u32 const index;

    void raise();
};

}}  // namespace Motor::World

#ifndef MOTOR_COMPUTE
#    include <motor/world/event/event.meta.factory.hh>
#endif

#endif
