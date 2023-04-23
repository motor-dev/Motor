/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/integer.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Integer::Integer(i64 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Integer::~Integer() = default;

ConversionCost Integer::distance(const Type& type) const
{
    return ConversionCalculator< i64 >::calculate(type);
}

void Integer::doEval(const Meta::Type& expectedType, Meta::Value& result) const
{
    if(motor_type< i8 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< i8 >(m_value));
    else if(motor_type< i16 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< i16 >(m_value));
    else if(motor_type< i32 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< i32 >(m_value));
    else if(motor_type< i64 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< i64 >(m_value));
    else if(motor_type< u8 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< u8 >(m_value));
    else if(motor_type< u16 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< u16 >(m_value));
    else if(motor_type< u32 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< u32 >(m_value));
    else if(motor_type< u64 >().isA(expectedType))
        result = Meta::Value(motor_checked_numcast< u64 >(m_value));
    else
        motor_notreached();
}

void Integer::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
