/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/int2.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Int2::Int2(bigint2 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Int2::~Int2()
{
}

ConversionCost Int2::distance(const Type& type) const
{
    return ConversionCalculator< bigint2 >::calculate(type);
}

void Int2::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< byte2 >().isA(expectedType))
        result = Meta::Value(make_byte2(motor_checked_numcast< i8 >(m_value[0]),
                                        motor_checked_numcast< i8 >(m_value[1])));
    else if(motor_type< short2 >().isA(expectedType))
        result = Meta::Value(make_short2(motor_checked_numcast< i16 >(m_value[0]),
                                         motor_checked_numcast< i16 >(m_value[1])));
    else if(motor_type< int2 >().isA(expectedType))
        result = Meta::Value(make_int2(motor_checked_numcast< i32 >(m_value[0]),
                                       motor_checked_numcast< i32 >(m_value[1])));
    else if(motor_type< bigint2 >().isA(expectedType))
        result = Meta::Value(make_bigint2(motor_checked_numcast< i64 >(m_value[0]),
                                          motor_checked_numcast< i64 >(m_value[1])));
    else if(motor_type< ushort2 >().isA(expectedType))
        result = Meta::Value(make_ushort2(motor_checked_numcast< u16 >(m_value[0]),
                                          motor_checked_numcast< u16 >(m_value[1])));
    else if(motor_type< uint2 >().isA(expectedType))
        result = Meta::Value(make_uint2(motor_checked_numcast< u32 >(m_value[0]),
                                        motor_checked_numcast< u32 >(m_value[1])));
    else if(motor_type< biguint2 >().isA(expectedType))
        result = Meta::Value(make_biguint2(motor_checked_numcast< u64 >(m_value[0]),
                                           motor_checked_numcast< u64 >(m_value[1])));
    else
        motor_notreached();
}

void Int2::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
