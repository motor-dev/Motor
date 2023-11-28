/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/namespace.hh>
#include <builtin-numbers.meta.hh>

namespace Motor { namespace Meta {

static void nullconstructor(const void* /*src*/, void* /*dst*/)
{
}

static void nulldestructor(void*)
{
}

static InterfaceTable s_emptyTable
    = {{nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr},
       {nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr}, nullptr};

template <>
MOTOR_EXPORT istring ClassID< void >::name()
{
    static const istring s_name("void");
    return s_name;
}

template <>
MOTOR_EXPORT raw< const Meta::Class > ClassID< void >::klass()
{
    static Meta::Class s_void = {name(),           0,
                                 {nullptr},        0,
                                 {nullptr},        {nullptr},
                                 {nullptr},        {nullptr},
                                 {nullptr},        {&s_emptyTable},
                                 &nullconstructor, &nulldestructor};
    return {&s_void};
}

template <>
MOTOR_EXPORT istring ClassID< minitl::pointer >::name()
{
    static const istring s_name("pointer");
    return s_name;
}

template <>
MOTOR_EXPORT raw< const Meta::Class > ClassID< minitl::pointer >::klass()
{
    static Meta::Class s_pointer = {name(),
                                    0,
                                    motor_class< void >(),
                                    0,
                                    {nullptr},
                                    {nullptr},
                                    {nullptr},
                                    {nullptr},
                                    {nullptr},
                                    motor_class< void >()->interfaces,
                                    &nullconstructor,
                                    &nulldestructor};
    return {&s_pointer};
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< i8 >::klass()
{
    return ClassID< motor_i8 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< i16 >::klass()
{
    return ClassID< motor_i16 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< i32 >::klass()
{
    return ClassID< motor_i32 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< i64 >::klass()
{
    return ClassID< motor_i64 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< u8 >::klass()
{
    return ClassID< motor_u8 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< u16 >::klass()
{
    return ClassID< motor_u16 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< u32 >::klass()
{
    return ClassID< motor_u32 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< u64 >::klass()
{
    return ClassID< motor_u64 >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< bool >::klass()
{
    return ClassID< motor_bool >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< float >::klass()
{
    return ClassID< motor_float >::klass();
}

template <>
MOTOR_EXPORT raw< const Class > ClassID< double >::klass()
{
    return ClassID< motor_double >::klass();
}

const ConversionCost ConversionCost::s_incompatible {0, 0, 0, 0, 1};
const ConversionCost ConversionCost::s_variant {0, 0, 0, 1, 0};

}}  // namespace Motor::Meta