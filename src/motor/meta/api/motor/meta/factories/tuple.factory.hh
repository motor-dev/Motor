/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_META_FACTORIES_TUPLE_FACTORY_HH
#define MOTOR_META_FACTORIES_TUPLE_FACTORY_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/builder.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename... T >
struct ClassID< minitl::tuple< T... > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(minitl::format< 2048u >(FMT("tuple<{0}>"), "TODO"));
        return s_name;
    }
};

template < typename... T >
MOTOR_EXPORT raw< const Meta::Class > ClassID< minitl::tuple< T... > >::klass()
{
    static const Meta::Class s_class = {name(),
                                        u32(sizeof(minitl::tuple< T... >)),
                                        {motor_class< void >().m_ptr},
                                        0,
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        motor_class< void >()->interfaces,
                                        &metaCopy< minitl::tuple< T... > >,
                                        &metaDestroy< minitl::tuple< T... > >};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

#endif
