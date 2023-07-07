/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_FACTORIES_CARRAY_FACTORY_HH
#define MOTOR_META_FACTORIES_CARRAY_FACTORY_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/operatortable.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T, u32 Count >
struct ClassID< T[Count] >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("{0}[{1}]"), TypeID< T >::name(), Count));
        return s_name;
    }
};

template < typename T, u32 Count >
struct ClassID< const T[Count] >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("{0}[{1}]"), TypeID< T >::name(), Count));
        return s_name;
    }
};

template < typename T, u32 Count >
struct carray_RTTIHelper
{
    typedef T ArrayType[Count];

    static const Meta::Type value_type;
    static u32              array_size(const Meta::Value& v);
    static Meta::Value      index(Meta::Value& v, u32 i);
    static Meta::Value      indexConst(const Meta::Value& v, u32 i);

    static Meta::Value                   trampoline_method_size_overload_0(Meta::Value* parameters,
                                                                           u32          parameterCount);
    static const Meta::Method::Parameter s_method_size_overload_0_params[];
    static const Meta::Method::Overload  s_method_size_overloads[];
    static Meta::Value                   trampoline_method_Index_overload_0(Meta::Value* parameters,
                                                                            u32          parameterCount);
    static const Meta::Method::Parameter s_method_Index_overload_0_params[];
    static Meta::Value                   trampoline_method_Index_overload_1(Meta::Value* parameters,
                                                                            u32          parameterCount);
    static const Meta::Method::Parameter s_method_Index_overload_1_params[];
    static const Meta::Method::Overload  s_method_Index_overloads[];
    static const Meta::Object            s_prop_value_type_object_value_type;
    static const Meta::ArrayOperatorTable scriptingArrayAPI;
    static const Meta::OperatorTable      scriptingAPI;
};

template < typename T, u32 Count >
const Meta::Type carray_RTTIHelper< T, Count >::value_type = motor_type< T >();

template < typename T, u32 Count >
u32 carray_RTTIHelper< T, Count >::array_size(const Meta::Value& v)
{
    motor_forceuse(v);
    return Count;
}

template < typename T, u32 Count >
Meta::Value carray_RTTIHelper< T, Count >::index(Meta::Value& v, u32 i)
{
    return Meta::Value(Meta::Value::ByRef(v.as< ArrayType& >()[i]));
}

template < typename T, u32 Count >
Meta::Value carray_RTTIHelper< T, Count >::indexConst(const Meta::Value& v, u32 i)
{
    return Meta::Value(Meta::Value::ByRef(v.as< const ArrayType& >()[i]));
}

template < typename T, u32 Count >
Meta::Value
carray_RTTIHelper< T, Count >::trampoline_method_size_overload_0(Meta::Value* parameters,
                                                                 u32          parameterCount)
{
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    return Meta::Value(Count);
}

template < typename T, u32 Count >
Meta::Value
carray_RTTIHelper< T, Count >::trampoline_method_Index_overload_0(Meta::Value* parameters,
                                                                  u32          parameterCount)
{
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    const ArrayType& array = parameters[0].as< const ArrayType& >();
    u32              index = parameters[1].as< u32 >();
    return Meta::Value(Meta::Value::ByRef(array[index]));
}

template < typename T, u32 Count >
Meta::Value
carray_RTTIHelper< T, Count >::trampoline_method_Index_overload_1(Meta::Value* parameters,
                                                                  u32          parameterCount)
{
    motor_forceuse(parameters);
    motor_forceuse(parameterCount);
    ArrayType& array = parameters[0].as< ArrayType& >();
    u32        index = parameters[1].as< u32 >();
    return Meta::Value(Meta::Value::ByRef(array[index]));
}

template < typename T, u32 Count >
const Meta::ObjectInfo carray_RTTIHelper< T, Count >::s_prop_value_type_object_value_type
    = {{nullptr}, {nullptr}, istring(istring("value_type")), Meta::Value(value_type)};

template < typename T, u32 Count >
const Meta::Method::Parameter carray_RTTIHelper< T, Count >::s_method_size_overload_0_params[]
    = {{{0},
        istring("this"),
        motor_type< const ArrayType& >(),
        Meta::Method::Parameter::noDefaultValue}};

template < typename T, u32 Count >
const Meta::Method::Overload carray_RTTIHelper< T, Count >::s_method_size_overloads[]
    = {{{0},
        {1, s_method_size_overload_0_params},
        motor_type< u32 >(),
        false,
        {0, 0},
        &trampoline_method_size_overload_0}};

template < typename T, u32 Count >
const Meta::Method::Parameter carray_RTTIHelper< T, Count >::s_method_Index_overload_0_params[]
    = {{{0},
        istring("this"),
        motor_type< const ArrayType& >(),
        Meta::Method::Parameter::noDefaultValue},
       {{0}, istring("index"), motor_type< u32 >(), Meta::Method::Parameter::noDefaultValue}};

template < typename T, u32 Count >
const Meta::Method::Parameter carray_RTTIHelper< T, Count >::s_method_Index_overload_1_params[]
    = {{{0}, istring("this"), motor_type< ArrayType& >(), Meta::Method::Parameter::noDefaultValue},
       {{0}, istring("index"), motor_type< u32 >(), Meta::Method::Parameter::noDefaultValue}};

template < typename T, u32 Count >
const Meta::Method::Overload carray_RTTIHelper< T, Count >::s_method_Index_overloads[]
    = {{{0},
        {2, s_method_Index_overload_0_params},
        motor_type< const T& >(),
        false,
        {0, 0},
        &trampoline_method_Index_overload_0},
       {{0},
        {2, s_method_Index_overload_1_params},
        motor_type< T& >(),
        false,
        {0, 0},
        &trampoline_method_Index_overload_1}};

template < typename T, u32 Count >
const Meta::ArrayOperatorTable carray_RTTIHelper< T, Count >::scriptingArrayAPI
    = {motor_type< T >(), &array_size, &index, &indexConst};

template < typename T, u32 Count >
const Meta::OperatorTable carray_RTTIHelper< T, Count >::scriptingAPI
    = {{&scriptingArrayAPI}, {0, nullptr}, {nullptr}};

template < typename T, u32 Count >
MOTOR_EXPORT raw< const Meta::Class > ClassID< T[Count] >::klass()
{
    /* work around Intel compiler issue
     * internal error: assertion failed: adjust_cleanup_state_for_aggregate_init: NULL dip
     * (shared/edgcpfe/lower_init.c, line 6280)
     */
    static const Meta::Method s_methods[2]
        = {{istring("size"),
            {1, carray_RTTIHelper< T, Count >::s_method_size_overloads},
            {&s_methods[1]}},
           {istring("Index"),
            {2, carray_RTTIHelper< T, Count >::s_method_Index_overloads},
            {&s_methods[2]}}};
    static const Meta::Class s_class = {name(),
                                        u32(sizeof(T[Count])),
                                        0,
                                        Meta::ClassType_Array,
                                        {0},
                                        {motor_class< void >().m_ptr},
                                        {0},
                                        {0},
                                        {0, 0},
                                        {2, s_methods},
                                        {0},
                                        {&carray_RTTIHelper< T, Count >::scriptingAPI},
                                        &Meta::wrap< T[Count] >::copy,
                                        &Meta::wrap< T[Count] >::destroy};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

template < typename T, u32 Count >
MOTOR_EXPORT raw< const Meta::Class > ClassID< const T[Count] >::klass()
{
    /* work around Intel compiler issue
     * internal error: assertion failed: adjust_cleanup_state_for_aggregate_init: NULL dip
     * (shared/edgcpfe/lower_init.c, line 6280)
     */
    static const Meta::Method s_methods[2]
        = {{istring("size"),
            {1, carray_RTTIHelper< const T, Count >::s_method_size_overloads},
            {&s_methods[1]}},
           {istring("Index"),
            {2, carray_RTTIHelper< const T, Count >::s_method_Index_overloads},
            {&s_methods[2]}}};
    static const Meta::Class s_class = {name(),
                                        u32(sizeof(const T[Count])),
                                        0,
                                        Meta::ClassType_Array,
                                        {0},
                                        {motor_class< void >().m_ptr},
                                        {0},
                                        {0},
                                        {0, 0},
                                        {2, s_methods},
                                        {0},
                                        {&carray_RTTIHelper< const T, Count >::scriptingAPI},
                                        &Meta::wrap< T[Count] >::copy,
                                        &Meta::wrap< const T[Count] >::destroy};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

}}  // namespace Motor::Meta

#endif
