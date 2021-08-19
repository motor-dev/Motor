/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/array.factory.hh>
#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/namespace.hh>

namespace Motor { namespace Meta {

template <>
MOTOR_EXPORT raw< const Meta::Class > ClassID< void >::klass()
{
    static Meta::Class s_void = {"void",
                                 0,
                                 0,
                                 0,
                                 {0},
                                 {0},
                                 {0},
                                 {0},
                                 {0, 0},
                                 {0, 0},
                                 {0},
                                 {0},
                                 &Meta::nullconstructor< 0 >,
                                 &Meta::nulldestructor};
    raw< Meta::Class > ci     = {&s_void};
    return ci;
}

template <>
MOTOR_EXPORT raw< const Meta::Class > ClassID< minitl::pointer >::klass()
{
    static Meta::Class s_pointer = {
        "pointer", 0,      0,      0,   {0}, {motor_class< void >().m_ptr}, {0},
        {0},       {0, 0}, {0, 0}, {0}, {0}, &Meta::nullconstructor< 0 >,   &Meta::nulldestructor};
    raw< Meta::Class > ci = {&s_pointer};
    return ci;
}

template <>
MOTOR_EXPORT raw< const Meta::Class > ClassID< minitl::refcountable >::klass()
{
    static Meta::Class s_refcountable = {"refcountable",
                                         0,
                                         0,
                                         0,
                                         {0},
                                         {motor_class< minitl::pointer >().m_ptr},
                                         {0},
                                         {0},
                                         {0, 0},
                                         {0, 0},
                                         {0},
                                         {0},
                                         &Meta::nullconstructor< 0 >,
                                         &Meta::nulldestructor};
    raw< Meta::Class > ci             = {&s_refcountable};
    return ci;
}

static Type s_numericTypes[]
    = {motor_type< bool >(), motor_type< u8 >(),    motor_type< u16 >(),   motor_type< u32 >(),
       motor_type< u64 >(),  motor_type< i8 >(),    motor_type< i16 >(),   motor_type< i32 >(),
       motor_type< i64 >(),  motor_type< float >(), motor_type< double >()};

static Type s_stringTypes[]
    = {motor_type< istring >(), motor_type< inamespace >(), motor_type< ifilename >(),
       motor_type< ipath >(), motor_type< text >()};

const Type& getTypeFromIndex(ClassIndex_Numeric index)
{
    return s_numericTypes[index];
}
const Type& getTypeFromIndex(ClassIndex_String index)
{
    return s_stringTypes[index];
}

}}  // namespace Motor::Meta
