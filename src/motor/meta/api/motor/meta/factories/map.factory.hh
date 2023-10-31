/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_META_FACTORIES_CARRAY_FACTORY_HH
#define MOTOR_META_FACTORIES_CARRAY_FACTORY_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/builder.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/minitl/hashmap.hh>

namespace Motor { namespace Meta {

template < typename T, u32 COUNT >
struct ClassID< T[COUNT] >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("{0}[{1}]"), TypeID< T >::name(), COUNT));
        return s_name;
    }
};

template < typename T, u32 COUNT >
MOTOR_EXPORT raw< const Meta::Class > ClassID< T[COUNT] >::klass()
{
    static const Meta::Class s_class = {name(),
                                        u32(sizeof(T[COUNT])),
                                        {motor_class< void >().m_ptr},
                                        0,
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        {nullptr},
                                        motor_class< void >()->interfaces,
                                        &metaCopy< T[COUNT] >,
                                        &metaDestroy< T[COUNT] >};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

#endif
