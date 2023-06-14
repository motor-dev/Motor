/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_ENGINE_TUPLE_FACTORY_HH
#define MOTOR_META_ENGINE_TUPLE_FACTORY_HH

#include <motor/meta/stdafx.h>
#include <motor/minitl/tuple.hh>

#include <motor/meta/engine/helper/getset.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

template < typename... T >
struct ClassID< minitl::tuple< T... > >
{
    static Value trampoline_method_tuple_overload_0(raw< const Method > method, Value* parameters,
                                                    u32 parameterCount);
    static Value trampoline_method_tuple_overload_1(raw< const Method > method, Value* parameters,
                                                    u32 parameterCount);

    static const Method::Parameter s_method_tuple_overload_1_params[];
    static const Method::Overload  s_method_tuple_overloads[];
    static const Meta::Method      s_methods[];

    MOTOR_EXPORT static raw< const Class > klass();
    MOTOR_EXPORT static istring            name()
    {
        static const istring s_name(minitl::format_buffer< 4096u > {"tuple<TODO:join>"});
        return s_name;
    }
};

template < typename... T >
MOTOR_EXPORT raw< const Class > ClassID< minitl::tuple< T... > >::klass()
{
    static const Class s_class = {/* .name */ name(),
                                  /* .size */ u32(sizeof(minitl::tuple< T... >)),
                                  /* .offset */ 0,
                                  /* .id */ ClassType_Struct,
                                  /* .owner */ {motor_motor_Namespace().m_ptr},
                                  /* .parent */ {motor_class< void >().m_ptr},
                                  /* .objects */ {0},
                                  /* .tags */ {0},
                                  /* .properties */ {0, 0},
                                  /* .methods */ {0, 0},
                                  /* .constructor */ {0},
                                  /* .operators */ OperatorTable::s_emptyTable,
                                  /* .copyconstructor */ &wrap< minitl::tuple< T... > >::copy,
                                  /* .destructor */ &wrap< minitl::tuple< T... > >::destroy};

    raw< const Class > result = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

#endif
