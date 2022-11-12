/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>
#include <motor/script.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Script< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {name(), u32(sizeof(Script< T >)),
               0,      Meta::ClassType_Object,
               {0},    motor_class< Resource::Description< T > >(),
               {0},    {0},
               {0, 0}, {0, 0},
               {0},    motor_class< Resource::Description< T > >()->operators,
               0,      0};
        raw< const Meta::Class > result = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Script<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta
