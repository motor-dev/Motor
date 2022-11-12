/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/int2.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Int2::Int2(knl::bigint2 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Int2::~Int2()
{
}

ConversionCost Int2::distance(const Type& type) const
{
    return ConversionCalculator< knl::bigint2 >::calculate(type);
}

void Int2::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< knl::byte2 >().isA(expectedType))
        result = Meta::Value(knl::make_byte2(motor_checked_numcast< i8 >(m_value[0]),
                                             motor_checked_numcast< i8 >(m_value[1])));
    else if(motor_type< knl::short2 >().isA(expectedType))
        result = Meta::Value(knl::make_short2(motor_checked_numcast< i16 >(m_value[0]),
                                              motor_checked_numcast< i16 >(m_value[1])));
    else if(motor_type< knl::int2 >().isA(expectedType))
        result = Meta::Value(knl::make_int2(motor_checked_numcast< i32 >(m_value[0]),
                                            motor_checked_numcast< i32 >(m_value[1])));
    else if(motor_type< knl::bigint2 >().isA(expectedType))
        result = Meta::Value(knl::make_bigint2(motor_checked_numcast< i64 >(m_value[0]),
                                               motor_checked_numcast< i64 >(m_value[1])));
    else if(motor_type< knl::ubyte2 >().isA(expectedType))
        result = Meta::Value(knl::make_ubyte2(motor_checked_numcast< u8 >(m_value[0]),
                                              motor_checked_numcast< u8 >(m_value[1])));
    else if(motor_type< knl::ushort2 >().isA(expectedType))
        result = Meta::Value(knl::make_ushort2(motor_checked_numcast< u16 >(m_value[0]),
                                               motor_checked_numcast< u16 >(m_value[1])));
    else if(motor_type< knl::uint2 >().isA(expectedType))
        result = Meta::Value(knl::make_uint2(motor_checked_numcast< u32 >(m_value[0]),
                                             motor_checked_numcast< u32 >(m_value[1])));
    else if(motor_type< knl::biguint2 >().isA(expectedType))
        result = Meta::Value(knl::make_biguint2(motor_checked_numcast< u64 >(m_value[0]),
                                                motor_checked_numcast< u64 >(m_value[1])));
    else
        motor_notreached();
}

void Int2::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
