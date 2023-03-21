/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_SCRIPT_FACTORY_HH_
#define MOTOR_MOTOR_SCRIPT_FACTORY_HH_
/**************************************************************************************************/
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
    static MOTOR_EXPORT raw< const Meta::Class > klass()
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
    static MOTOR_EXPORT istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Script<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
