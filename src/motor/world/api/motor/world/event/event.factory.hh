/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_EVENT_EVENT_FACTORY_HH
#define MOTOR_WORLD_EVENT_EVENT_FACTORY_HH
#pragma once

#include <motor/world/event/event.hh>

#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T1, typename T2, typename T3, typename T4 >
struct ClassID< World::Event< T1, T2, T3, T4 > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(minitl::format< 2048u >(
            FMT("Event<{0},{1},{2},{3}>"), TypeID< T1 >::name(), TypeID< T2 >::name(),
            TypeID< T3 >::name(), TypeID< T4 >::name()));
        return s_name;
    }
};

template < typename T1, typename T2, typename T3, typename T4 >
MOTOR_EXPORT raw< const Meta::Class > ClassID< World::Event< T1, T2, T3, T4 > >::klass()
{
    static const Meta::Class s_class = {/* .name */ name(),
                                        /* .size */ u32(sizeof(World::Event< T1, T2, T3, T4 >)),
                                        /* .parent */ motor_class< void >(),
                                        /* .offset */ 0,
                                        /* .objects */ motor_class< void >()->objects,
                                        /* .tags */ motor_class< void >()->tags,
                                        /* .properties */ motor_class< void >()->properties,
                                        /* .methods */ motor_class< void >()->methods,
                                        /* .constructor */ {nullptr},
                                        /* .operators */ motor_class< void >()->interfaces,
                                        /* .copyconstructor */ nullptr,
                                        /* .destructor */ nullptr};

    raw< const Meta::Class > result = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

#endif
