/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_WORLD_EVENT_EVENT_HH_
#define MOTOR_WORLD_WORLD_EVENT_EVENT_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

#ifndef MOTOR_COMPUTE

namespace Motor { namespace World {

template < typename T1 = void, typename T2 = void, typename T3 = void, typename T4 = void >
struct Event
{
public:
    u32 const index;

    void raise();
};

}}  // namespace Motor::World

#    include <motor/world/event/event.factory.hh>

#else

namespace Motor { namespace World {

template < typename T1 = void, typename T2 = void, typename T3 = void, typename T4 = void >
struct Event
{
public:
    u32 const index;

    void raise();
};

}}  // namespace Motor::World

#endif

/**************************************************************************************************/
#endif
