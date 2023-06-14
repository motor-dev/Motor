/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH
#define MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH

#include <motor/resource/description.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Resource::Description< T > >
{
    static const Meta::OperatorTable             s_operatorTable;
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(Resource::Description< T >)),
                                            0,
                                            Meta::ClassType_Object,
                                            {nullptr},
                                            motor_class< Resource::IDescription >(),
                                            {nullptr},
                                            {nullptr},
                                            {0, nullptr},
                                            {0, nullptr},
                                            {nullptr},
                                            {&s_operatorTable},
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
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

#endif
