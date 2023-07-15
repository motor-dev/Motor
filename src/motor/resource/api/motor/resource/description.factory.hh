/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH
#define MOTOR_RESOURCE_DESCRIPTION_FACTORY_HH
#pragma once

#include <motor/resource/description.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Resource::Description< T > >
{
    static const Meta::InterfaceTable            s_interfaceTable;
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
                                            {&s_interfaceTable},
                                            nullptr,
                                            nullptr};
        return {&s_class};
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Description<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

template < typename T >
const Meta::InterfaceTable ClassID< Resource::Description< T > >::s_interfaceTable
    = {motor_class< Resource::IDescription >()->interfaces->boolInterface,
       motor_class< Resource::IDescription >()->interfaces->i64Interface,
       motor_class< Resource::IDescription >()->interfaces->u64Interface,
       motor_class< Resource::IDescription >()->interfaces->floatInterface,
       motor_class< Resource::IDescription >()->interfaces->doubleInterface,
       motor_class< Resource::IDescription >()->interfaces->charpInterface,
       motor_class< Resource::IDescription >()->interfaces->variantInterface,
       motor_class< Resource::IDescription >()->interfaces->arrayInterface,
       motor_class< Resource::IDescription >()->interfaces->mapInterface,
       motor_class< T >(),
       motor_class< Resource::IDescription >()->interfaces->call,
       motor_class< Resource::IDescription >()->interfaces->dynamicCall};

}}  // namespace Motor::Meta

#endif
