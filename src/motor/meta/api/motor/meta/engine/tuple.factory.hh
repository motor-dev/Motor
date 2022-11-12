/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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

namespace {

template < typename T, u32 I >
struct ClassIDTupleHelperPair
{
    static constexpr u32 Index = I;
    typedef T            Type;
};

template < u32 INDEX, typename... TAIL >
struct ClassIDTupleHelper;

template < u32 INDEX, typename T, typename... TAIL >
struct ClassIDTupleHelper< INDEX, T, TAIL... >
{
    static constexpr u32 ParamCount = 1 + ClassIDTupleHelper< INDEX + 1, TAIL... >::ParamCount;
    template < typename... PAIRS >
    struct ClassIDTupleIndexedHelper
        : public ClassIDTupleHelper< INDEX + 1, TAIL... >::template ClassIDTupleIndexedHelper<
              PAIRS..., ClassIDTupleHelperPair< T, INDEX > >
    {
        static ObjectInfo s_propertyType;
    };
};

template < u32 INDEX, typename T, typename... TAIL >
template < typename... PAIRS >
ObjectInfo
    ClassIDTupleHelper< INDEX, T, TAIL... >::ClassIDTupleIndexedHelper< PAIRS... >::s_propertyType
    = {{&ClassIDTupleHelper< INDEX + 1, TAIL... >::template ClassIDTupleIndexedHelper<
           ClassIDTupleHelperPair< T, INDEX >, PAIRS... >::s_propertyType},
       {0},
       istring(minitl::format< 128u >("type_%d") | INDEX),
       Value(motor_type< T >())};

template < u32 INDEX, typename T >
struct ClassIDTupleHelper< INDEX, T >
{
    static constexpr u32 ParamCount = 1;
    template < typename... PAIRS >
    struct ClassIDTupleIndexedHelper
        : public ClassIDTupleHelper< INDEX + 1 >::template ClassIDTupleIndexedHelper<
              PAIRS..., ClassIDTupleHelperPair< T, INDEX > >
    {
        static ObjectInfo s_propertyType;
    };
};

template < u32 INDEX, typename T >
template < typename... PAIRS >
ObjectInfo ClassIDTupleHelper< INDEX, T >::ClassIDTupleIndexedHelper< PAIRS... >::s_propertyType
    = {{0}, {0}, istring(minitl::format< 128u >("type_%d") | INDEX), Value(motor_type< T >())};

template < u32 INDEX >
struct ClassIDTupleHelper< INDEX >
{
    static constexpr u32 ParamCount = 1;
    template < typename... PAIRS >
    struct ClassIDTupleIndexedHelper
    {
        static Method::Parameter                         s_constructorParameter[];
        static ObjectInfo                                s_propertyType;
        static Property                                  s_properties[];
        typedef minitl::tuple< typename PAIRS::Type... > Owner;
        template < u32 I >
        static Value get(raw< const Property > property, void* from)
        {
            motor_forceuse(property);
            const Owner* owner = reinterpret_cast< const Owner* >(from);
            return Value::ByRef(minitl::get< I >(*owner));
        }
        template < u32 I >
        static void set(raw< const Property > property, void* from, const Value& value)
        {
            motor_forceuse(property);
            Owner* owner = reinterpret_cast< Owner* >(from);
            minitl::get< I >(*owner)
                = value.as< const typename Owner::template member_type_t< I >& >();
        }
        static Value construct(Value* parameters, u32 parameterCount)
        {
            motor_assert(parameterCount == INDEX,
                         "incorrect parameter count; expected %d, received %d" | INDEX
                             | parameterCount);
            return Value(minitl::tuple< typename PAIRS::Type... >(
                parameters[PAIRS::Index].template as< const typename PAIRS::Type& >()...));
        }
    };
};

template < u32 INDEX >
template < typename... PAIRS >
Method::Parameter
    ClassIDTupleHelper< INDEX >::ClassIDTupleIndexedHelper< PAIRS... >::s_constructorParameter[]
    = {{{0},
        istring(minitl::format< 128u >("_%d") | PAIRS::Index),
        motor_type< typename PAIRS::Type >(),
        {&Method::Parameter::s_noDefaultValue}}...};

template < u32 INDEX >
template < typename... PAIRS >
Property ClassIDTupleHelper< INDEX >::ClassIDTupleIndexedHelper< PAIRS... >::s_properties[]
    = {{{0},
        istring(minitl::format< 128u >("_%d") | PAIRS::Index),
        motor_type< minitl::tuple< typename PAIRS::Type... > >(),
        motor_type< typename PAIRS::Type >(),
        &get< PAIRS::Index >,
        &set< PAIRS::Index >}...};

}  // namespace

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
        static const istring s_name(minitl::format< 4096u >("tuple<TODO>"));
        return s_name;
    }
};

template < typename... T >
Value ClassID< minitl::tuple< T... > >::trampoline_method_tuple_overload_0(
    raw< const Method > method, Value* parameters, u32 parameterCount)
{
    motor_forceuse(method);
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    return Value(minitl::tuple< T... >());
}

template < typename... T >
Value ClassID< minitl::tuple< T... > >::trampoline_method_tuple_overload_1(
    raw< const Method > method, Value* parameters, u32 parameterCount)
{
    motor_forceuse(method);
    return ClassIDTupleHelper< 0, T... >::template ClassIDTupleIndexedHelper<>::construct(
        parameters, parameterCount);
}

template < typename... T >
const Method::Overload ClassID< minitl::tuple< T... > >::s_method_tuple_overloads[] = {
    {{0},
     {0, 0},
     motor_type< minitl::tuple< T... > >(),
     false,
     &trampoline_method_tuple_overload_0},
    {{0},
     {ClassIDTupleHelper< 0, T... >::ParamCount,
      ClassIDTupleHelper< 0, T... >::template ClassIDTupleIndexedHelper<>::s_constructorParameter},
     motor_type< minitl::tuple< T... > >(),
     false,
     &trampoline_method_tuple_overload_1}};

template < typename... T >
const Method ClassID< minitl::tuple< T... > >::s_methods[1]
    = {{istring("tuple"), {2, s_method_tuple_overloads}, {&s_methods[0]}}};

template < typename... T >
MOTOR_EXPORT raw< const Class > ClassID< minitl::tuple< T... > >::klass()
{
    static const Class s_class
        = {/* .name */ name(),
           /* .size */ u32(sizeof(minitl::tuple< T... >)),
           /* .offset */ 0,
           /* .id */ ClassType_Struct,
           /* .owner */ {motor_motor_Namespace().m_ptr},
           /* .parent */ {motor_class< void >().m_ptr},
           /* .objects */
           {&ClassIDTupleHelper< 0, T... >::template ClassIDTupleIndexedHelper<>::s_propertyType},
           /* .tags */ {0},
           /* .properties */
           {ClassIDTupleHelper< 0, T... >::ParamCount,
            ClassIDTupleHelper< 0, T... >::template ClassIDTupleIndexedHelper<>::s_properties},
           /* .methods */ {1, ClassID< minitl::tuple< T... > >::s_methods},
           /* .constructor */ {ClassID< minitl::tuple< T... > >::s_methods},
           /* .operators */ OperatorTable::s_emptyTable,
           /* .copyconstructor */ &wrap< minitl::tuple< T... > >::copy,
           /* .destructor */ &wrap< minitl::tuple< T... > >::destroy};

    raw< const Class > result = {&s_class};
    return result;
}

}}  // namespace Motor::Meta
