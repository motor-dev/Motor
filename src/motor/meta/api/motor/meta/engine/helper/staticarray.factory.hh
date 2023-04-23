/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/typeinfo.meta.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< Meta::staticarray< T > >
{
    static const Meta::Type value_type;
    static u32              array_size(const Meta::Value& v);
    static Meta::Value      index(Meta::Value& v, u32 i);
    static Meta::Value      indexConst(const Meta::Value& v, u32 i);

    static Meta::Value callStaticArrayOperatorIndex(raw< const Meta::Method > method,
                                                    Meta::Value* params, u32 paramCount);
    static Meta::Value callStaticArraySize(raw< const Meta::Method > method, Meta::Value* params,
                                           u32 paramCount);
    static Meta::Value callStaticArrayOperatorIndexConst(raw< const Meta::Method > method,
                                                         Meta::Value* params, u32 paramCount);

    static const Meta::Method::Parameter  s_index_0_params[2];
    static const Meta::Method::Parameter  s_index_1_params[2];
    static const Meta::Method::Overload   s_method_index_overloads[2];
    static const Meta::Method::Parameter  s_size_params[1];
    static const Meta::Method::Overload   s_method_size_overloads[1];
    static const Meta::ArrayOperatorTable scriptingArrayAPI;
    static const Meta::OperatorTable      scriptingAPI;

    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("staticarray<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

template < typename T >
const Meta::Type ClassID< Meta::staticarray< T > >::value_type = motor_type< T >();

template < typename T >
u32 ClassID< Meta::staticarray< T > >::array_size(const Meta::Value& v)
{
    return v.as< const Meta::staticarray< T >& >().count;
}

template < typename T >
Meta::Value ClassID< Meta::staticarray< T > >::index(Meta::Value& v, u32 i)
{
    return Meta::Value(Meta::Value::ByRef(v.as< Meta::staticarray< T >& >().operator[](i)));
}

template < typename T >
Meta::Value ClassID< Meta::staticarray< T > >::indexConst(const Meta::Value& v, u32 i)
{
    return Meta::Value(Meta::Value::ByRef(v.as< const Meta::staticarray< T >& >().operator[](i)));
}

template < typename T >
Meta::Value
ClassID< Meta::staticarray< T > >::callStaticArrayOperatorIndex(raw< const Meta::Method > method,
                                                                Meta::Value* params, u32 paramCount)
{
    motor_forceuse(method);
    motor_assert_format(paramCount == 1, "expected 1 parameter; received {0}", paramCount);
    return Meta::Value(params[0].as< Meta::staticarray< T >& >().operator[](params[1].as< u32 >()));
}

template < typename T >
Meta::Value ClassID< Meta::staticarray< T > >::callStaticArraySize(raw< const Meta::Method > method,
                                                                   Meta::Value*              params,
                                                                   u32 paramCount)
{
    motor_forceuse(method);
    motor_assert_format(paramCount == 1, "expected 1 parameter; received {0}", paramCount);
    return Meta::Value(params[0].as< const Meta::staticarray< T >& >().count);
}

template < typename T >
Meta::Value ClassID< Meta::staticarray< T > >::callStaticArrayOperatorIndexConst(
    raw< const Meta::Method > method, Meta::Value* params, u32 paramCount)
{
    motor_forceuse(method);
    motor_assert_format(paramCount == 2, "expected 2 parameter; received {0}", paramCount);
    return Meta::Value(
        params[0].as< const Meta::staticarray< T >& >().operator[](params[1].as< u32 >()));
}

template < typename T >
const Meta::Method::Parameter ClassID< Meta::staticarray< T > >::s_index_0_params[2] = {
    {{0},
     istring("this"),
     motor_type< Meta::staticarray< T >& >(),
     ::Motor::Meta::Method::Parameter::noDefaultValue},
    {{0}, istring("index"), motor_type< u32 >(), ::Motor::Meta::Method::Parameter::noDefaultValue}};

template < typename T >
const Meta::Method::Parameter ClassID< Meta::staticarray< T > >::s_index_1_params[2] = {
    {{0},
     istring("this"),
     motor_type< const Meta::staticarray< T >& >(),
     ::Motor::Meta::Method::Parameter::noDefaultValue},
    {{0}, istring("index"), motor_type< u32 >(), ::Motor::Meta::Method::Parameter::noDefaultValue}};

template < typename T >
const Meta::Method::Overload ClassID< Meta::staticarray< T > >::s_method_index_overloads[2]
    = {{{0},
        {2, s_index_0_params},
        motor_type< const T& >(),
        false,
        &callStaticArrayOperatorIndexConst},
       {{0}, {2, s_index_1_params}, motor_type< T& >(), false, &callStaticArrayOperatorIndex}};

template < typename T >
const Meta::Method::Parameter ClassID< Meta::staticarray< T > >::s_size_params[1]
    = {{{0},
        istring("this"),
        motor_type< const Meta::staticarray< T >& >(),
        ::Motor::Meta::Method::Parameter::noDefaultValue}};

template < typename T >
const Meta::Method::Overload ClassID< Meta::staticarray< T > >::s_method_size_overloads[1]
    = {{{0}, {1, s_size_params}, motor_type< u32 >(), false, &callStaticArraySize}};

template < typename T >
const Meta::ArrayOperatorTable ClassID< Meta::staticarray< T > >::scriptingArrayAPI
    = {value_type, &array_size, &index, &indexConst};

template < typename T >
const Meta::OperatorTable ClassID< Meta::staticarray< T > >::scriptingAPI
    = {{&scriptingArrayAPI}, {0, 0}, {0}};

template < typename T >
MOTOR_EXPORT raw< const Meta::Class > ClassID< Meta::staticarray< T > >::klass()
{
    /* work around Intel compiler issue
     * internal error: assertion failed: adjust_cleanup_state_for_aggregate_init: NULL dip
     * (shared/edgcpfe/lower_init.c, line 6280)
     */
    static const Meta::Method s_methods[2]
        = {{Meta::Class::nameOperatorIndex(),
            {2, ClassID< Meta::staticarray< T > >::s_method_index_overloads},
            {&s_methods[0]}},
           {istring("size"),
            {1, ClassID< Meta::staticarray< T > >::s_method_size_overloads},
            {&s_methods[1]}}};
    static const ::Motor::Meta::Class s_class = {name(),
                                                 u32(sizeof(Meta::staticarray< T >)),
                                                 0,
                                                 Meta::ClassType_Array,
                                                 {motor_motor_Namespace().m_ptr},
                                                 {motor_class< void >().m_ptr},
                                                 {0},
                                                 {0},
                                                 {0, 0},
                                                 {2, s_methods},
                                                 {0},
                                                 {&ClassID< Meta::staticarray< T > >::scriptingAPI},
                                                 &Meta::wrap< Meta::staticarray< T > >::copy,
                                                 &Meta::wrap< Meta::staticarray< T > >::destroy};
    raw< const Meta::Class >          result  = {&s_class};
    return result;
}

}}  // namespace Motor::Meta
