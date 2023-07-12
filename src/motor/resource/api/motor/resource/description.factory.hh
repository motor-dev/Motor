/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH
#define MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH
#pragma once

#include <motor/resource/description.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/operatortable.hh>
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
                                            motor_class< Resource::IDescription >(),
                                            0,
                                            motor_class< Resource::IDescription >()->objects,
                                            motor_class< Resource::IDescription >()->tags,
                                            motor_class< Resource::IDescription >()->properties,
                                            motor_class< Resource::IDescription >()->methods,
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
    = {motor_class< Resource::IDescription >()->operators->boolOperators,
       motor_class< Resource::IDescription >()->operators->signedIntegerOperators,
       motor_class< Resource::IDescription >()->operators->unsignedIntegerOperators,
       motor_class< Resource::IDescription >()->operators->floatOperators,
       motor_class< Resource::IDescription >()->operators->doubleOperators,
       motor_class< Resource::IDescription >()->operators->stringOperators,
       motor_class< Resource::IDescription >()->operators->variantOperators,
       motor_class< Resource::IDescription >()->operators->arrayOperators,
       motor_class< Resource::IDescription >()->operators->mapOperators,
       motor_class< T >(),
       motor_class< Resource::IDescription >()->operators->call,
       motor_class< Resource::IDescription >()->operators->dynamicCall};

}}  // namespace Motor::Meta

#endif
