/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH_
#define MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/resource/description.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Resource::Description< T > >
{
    static const Meta::OperatorTable s_operatorTable;
    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(), u32(sizeof(Resource::Description< T >)),
                                            0,      Meta::ClassType_Object,
                                            {0},    motor_class< Resource::IDescription >(),
                                            {0},    {0},
                                            {0, 0}, {0, 0},
                                            {0},    {&s_operatorTable},
                                            0,      0};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    static MOTOR_EXPORT istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Description<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

template < typename T >
const Meta::OperatorTable ClassID< Resource::Description< T > >::s_operatorTable
    = {{0}, {0, 0}, motor_class< T >()};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
