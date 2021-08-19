/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/int4.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Int4::Int4(bigint4 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Int4::~Int4()
{
}

ConversionCost Int4::distance(const Type& type) const
{
    return ConversionCalculator< bigint4 >::calculate(type);
}

void Int4::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< byte4 >().isA(expectedType))
        result = Meta::Value(make_byte4(
            motor_checked_numcast< i8 >(m_value[0]), motor_checked_numcast< i8 >(m_value[1]),
            motor_checked_numcast< i8 >(m_value[2]), motor_checked_numcast< i8 >(m_value[3])));
    else if(motor_type< short4 >().isA(expectedType))
        result = Meta::Value(make_short4(
            motor_checked_numcast< i16 >(m_value[0]), motor_checked_numcast< i16 >(m_value[1]),
            motor_checked_numcast< i16 >(m_value[2]), motor_checked_numcast< i16 >(m_value[3])));
    else if(motor_type< int4 >().isA(expectedType))
        result = Meta::Value(make_int4(
            motor_checked_numcast< i32 >(m_value[0]), motor_checked_numcast< i32 >(m_value[1]),
            motor_checked_numcast< i32 >(m_value[2]), motor_checked_numcast< i32 >(m_value[3])));
    else if(motor_type< bigint4 >().isA(expectedType))
        result = Meta::Value(make_bigint4(
            motor_checked_numcast< i64 >(m_value[0]), motor_checked_numcast< i64 >(m_value[1]),
            motor_checked_numcast< i64 >(m_value[2]), motor_checked_numcast< i64 >(m_value[3])));
    else if(motor_type< ushort4 >().isA(expectedType))
        result = Meta::Value(make_ushort4(
            motor_checked_numcast< u16 >(m_value[0]), motor_checked_numcast< u16 >(m_value[1]),
            motor_checked_numcast< u16 >(m_value[2]), motor_checked_numcast< u16 >(m_value[3])));
    else if(motor_type< uint4 >().isA(expectedType))
        result = Meta::Value(make_uint4(
            motor_checked_numcast< u32 >(m_value[0]), motor_checked_numcast< u32 >(m_value[1]),
            motor_checked_numcast< u32 >(m_value[2]), motor_checked_numcast< u32 >(m_value[3])));
    else if(motor_type< biguint4 >().isA(expectedType))
        result = Meta::Value(make_biguint4(
            motor_checked_numcast< u64 >(m_value[0]), motor_checked_numcast< u64 >(m_value[1]),
            motor_checked_numcast< u64 >(m_value[2]), motor_checked_numcast< u64 >(m_value[3])));
    else
        motor_notreached();
}

void Int4::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
