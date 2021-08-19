/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_HELPER_TUPLE3_HH_
#define MOTOR_META_ENGINE_HELPER_TUPLE3_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/helper/get.hh>
#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/methodinfo.script.hh>
#include <motor/meta/engine/objectinfo.script.hh>
#include <motor/meta/engine/propertyinfo.script.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/minitl/tuple.hh>

namespace Motor { namespace Meta {

template < typename T1, typename T2, typename T3 >
struct ClassID< minitl::tuple< T1, T2, T3 > >
{
    static Meta::Value                   trampoline_method_tuple_overload_0(Meta::Value* parameters,
                                                                            u32          parameterCount);
    static Meta::Value                   trampoline_method_tuple_overload_1(Meta::Value* parameters,
                                                                            u32          parameterCount);
    static const Meta::Method::Parameter s_method_tuple_overload_1_params[];
    static const Meta::Method::Overload  s_method_tuple_overloads[];
    static const Meta::Method            s_methods[];
    static const Meta::Property          s_properties[];
    static const Meta::ObjectInfo        s_first_type_object_first_type;
    static const Meta::ObjectInfo        s_second_type_object_second_type;
    static const Meta::ObjectInfo        s_third_type_object_third_type;

    static MOTOR_EXPORT raw< const Meta::Class > klass();
};

template < typename T1, typename T2, typename T3 >
Meta::Value
ClassID< minitl::tuple< T1, T2, T3 > >::trampoline_method_tuple_overload_0(Meta::Value* parameters,
                                                                           u32 parameterCount)
{
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    return Meta::Value(minitl::tuple< T1, T2, T3 >());
}

template < typename T1, typename T2, typename T3 >
Meta::Value
ClassID< minitl::tuple< T1, T2, T3 > >::trampoline_method_tuple_overload_1(Meta::Value* parameters,
                                                                           u32 parameterCount)
{
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    return Meta::Value(minitl::tuple< T1, T2, T3 >(parameters[0].as< const T1& >(),
                                                   parameters[1].as< const T2& >(),
                                                   parameters[2].as< const T3& >()));
}

template < typename T1, typename T2, typename T3 >
const Meta::ObjectInfo ClassID< minitl::tuple< T1, T2, T3 > >::s_third_type_object_third_type
    = {{0}, {0}, istring(istring("third_type")), Meta::Value(motor_type< T3 >())};

template < typename T1, typename T2, typename T3 >
const Meta::ObjectInfo ClassID< minitl::tuple< T1, T2, T3 > >::s_second_type_object_second_type
    = {{&s_third_type_object_third_type},
       {0},
       istring(istring("second_type")),
       Meta::Value(motor_type< T2 >())};

template < typename T1, typename T2, typename T3 >
const Meta::ObjectInfo ClassID< minitl::tuple< T1, T2, T3 > >::s_first_type_object_first_type
    = {{&s_second_type_object_second_type},
       {0},
       istring(istring("first_type")),
       Meta::Value(motor_type< T1 >())};

template < typename T1, typename T2, typename T3 >
const Meta::Method::Parameter
    ClassID< minitl::tuple< T1, T2, T3 > >::s_method_tuple_overload_1_params[]
    = {{{0}, istring("first"), motor_type< T1 >(), {&Meta::Method::Parameter::s_noDefaultValue}},
       {{0}, istring("second"), motor_type< T2 >(), {&Meta::Method::Parameter::s_noDefaultValue}},
       {{0}, istring("third"), motor_type< T3 >(), {&Meta::Method::Parameter::s_noDefaultValue}}};

template < typename T1, typename T2, typename T3 >
const Meta::Method::Overload ClassID< minitl::tuple< T1, T2, T3 > >::s_method_tuple_overloads[]
    = {{{0},
        {0, 0},
        motor_type< minitl::tuple< T1, T2, T3 > >(),
        false,
        {0, 0},
        &trampoline_method_tuple_overload_0},
       {{0},
        {3, s_method_tuple_overload_1_params},
        motor_type< minitl::tuple< T1, T2, T3 > >(),
        false,
        {0, 0},
        &trampoline_method_tuple_overload_1}};

template < typename T1, typename T2, typename T3 >
const Meta::Method ClassID< minitl::tuple< T1, T2, T3 > >::s_methods[1]
    = {{istring("tuple"), {2, s_method_tuple_overloads}, {&s_methods[0]}}};

template < typename T1, typename T2, typename T3 >
const Meta::Property ClassID< minitl::tuple< T1, T2, T3 > >::s_properties[3]
    = {{{0},
        istring("first"),
        motor_type< minitl::tuple< T1, T2, T3 > >(),
        motor_type< T1 >(),
        &Meta::PropertyHelper< T1, minitl::tuple< T1, T2, T3 >,
                               &minitl::tuple< T1, T2, T3 >::first >::get},
       {{0},
        istring("second"),
        motor_type< minitl::tuple< T1, T2, T3 > >(),
        motor_type< T2 >(),
        &Meta::PropertyHelper< T2, minitl::tuple< T1, T2, T3 >,
                               &minitl::tuple< T1, T2, T3 >::second >::get},
       {{0},
        istring("third"),
        motor_type< minitl::tuple< T1, T2, T3 > >(),
        motor_type< T3 >(),
        &Meta::PropertyHelper< T3, minitl::tuple< T1, T2, T3 >,
                               &minitl::tuple< T1, T2, T3 >::third >::get}};

template < typename T1, typename T2, typename T3 >
MOTOR_EXPORT raw< const Meta::Class > ClassID< minitl::tuple< T1, T2, T3 > >::klass()
{
    static const Meta::Class s_class = {
        /* .name */ istring(minitl::format< 1024u >("tuple<%s,%s,%s>") | motor_type< T1 >().name()
                            | motor_type< T2 >().name() | motor_type< T3 >().name()),
        /* .size */ u32(sizeof(minitl::tuple< T1, T2, T3 >)),
        /* .offset */ 0,
        /* .id */ Meta::ClassType_Struct,
        /* .owner */ {motor_motor_Namespace().m_ptr},
        /* .parent */ {motor_class< void >().m_ptr},
        /* .objects */ {&ClassID< minitl::tuple< T1, T2, T3 > >::s_first_type_object_first_type},
        /* .tags */ {0},
        /* .properties */ {3, ClassID< minitl::tuple< T1, T2, T3 > >::s_properties},
        /* .methods */ {1, ClassID< minitl::tuple< T1, T2, T3 > >::s_methods},
        /* .constructor */ {ClassID< minitl::tuple< T1, T2, T3 > >::s_methods},
        /* .apiMethods */ {0},
        /* .copyconstructor */ &Meta::wrap< minitl::tuple< T1, T2, T3 > >::copy,
        /* .destructor */ &Meta::wrap< minitl::tuple< T1, T2, T3 > >::destroy};

    raw< const Meta::Class > result = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
