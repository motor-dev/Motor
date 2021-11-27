/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_EVENT_EVENT_FACTORY_HH_
#define MOTOR_WORLD_EVENT_EVENT_FACTORY_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/world/event/event.hh>

#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor {

MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace_Motor_World();

}

namespace Motor { namespace Meta {

template < typename T1, typename T2, typename T3, typename T4 >
struct ClassID< World::Event< T1, T2, T3, T4 > >
{
    static MOTOR_EXPORT raw< const Meta::Class > klass();
};

template < typename T1, typename T2, typename T3, typename T4 >
MOTOR_EXPORT raw< const Meta::Class > ClassID< World::Event< T1, T2, T3, T4 > >::klass()
{
    static const Meta::Class s_class
        = {/* .name */ istring(minitl::format< 1024u >("Event<%s,%s,%s,%s>")
                               | motor_type< T1 >().name() | motor_type< T2 >().name()
                               | motor_type< T3 >().name() | motor_type< T4 >().name()),
           /* .size */ u32(sizeof(World::Event< T1, T2, T3, T4 >)),
           /* .offset */ 0,
           /* .id */ Meta::ClassType_Struct,
           /* .owner */ {motor_motor_Namespace_Motor_World().m_ptr},
           /* .parent */ {motor_class< void >().m_ptr},
           /* .objects */ {0},
           /* .tags */ {0},
           /* .properties */ {0, 0},
           /* .methods */ {0, 0},
           /* .constructor */ {0},
           /* .operators */ Meta::OperatorTable::s_emptyTable,
           /* .copyconstructor */ 0,
           /* .destructor */ 0};

    raw< const Meta::Class > result = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
