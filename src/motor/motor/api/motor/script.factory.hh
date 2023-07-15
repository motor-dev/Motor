/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MOTOR_SCRIPT_FACTORY_HH
#define MOTOR_MOTOR_SCRIPT_FACTORY_HH
#pragma once

#include <motor/stdafx.h>
#include <motor/script.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Script< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(Script< T >)),
                                            motor_class< Resource::Description< T > >(),
                                            0,
                                            motor_class< Resource::Description< T > >()->objects,
                                            motor_class< Resource::Description< T > >()->tags,
                                            motor_class< Resource::Description< T > >()->properties,
                                            motor_class< Resource::Description< T > >()->methods,
                                            {nullptr},
                                            motor_class< Resource::Description< T > >()->interfaces,
                                            0,
                                            0};
        return {&s_class};
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Script<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
