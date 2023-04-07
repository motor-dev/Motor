/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/int3.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Int3::Int3(knl::bigint3 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Int3::~Int3()
{
}

ConversionCost Int3::distance(const Type& type) const
{
    return ConversionCalculator< knl::bigint3 >::calculate(type);
}

void Int3::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< knl::byte3 >().isA(expectedType))
        result = Meta::Value(knl::byte3 {motor_checked_numcast< i8 >(m_value._0),
                                         motor_checked_numcast< i8 >(m_value._1),
                                         motor_checked_numcast< i8 >(m_value._2)});
    else if(motor_type< knl::short3 >().isA(expectedType))
        result = Meta::Value(knl::short3 {motor_checked_numcast< i16 >(m_value._0),
                                          motor_checked_numcast< i16 >(m_value._1),
                                          motor_checked_numcast< i16 >(m_value._2)});
    else if(motor_type< knl::int3 >().isA(expectedType))
        result = Meta::Value(knl::int3 {motor_checked_numcast< i32 >(m_value._0),
                                        motor_checked_numcast< i32 >(m_value._1),
                                        motor_checked_numcast< i32 >(m_value._2)});
    else if(motor_type< knl::bigint3 >().isA(expectedType))
        result = Meta::Value(knl::bigint3 {motor_checked_numcast< i64 >(m_value._0),
                                           motor_checked_numcast< i64 >(m_value._1),
                                           motor_checked_numcast< i64 >(m_value._2)});
    else if(motor_type< knl::ubyte3 >().isA(expectedType))
        result = Meta::Value(knl::ubyte3 {motor_checked_numcast< u8 >(m_value._0),
                                          motor_checked_numcast< u8 >(m_value._1),
                                          motor_checked_numcast< u8 >(m_value._2)});
    else if(motor_type< knl::ushort3 >().isA(expectedType))
        result = Meta::Value(knl::ushort3 {motor_checked_numcast< u16 >(m_value._0),
                                           motor_checked_numcast< u16 >(m_value._1),
                                           motor_checked_numcast< u16 >(m_value._2)});
    else if(motor_type< knl::uint3 >().isA(expectedType))
        result = Meta::Value(knl::uint3 {motor_checked_numcast< u32 >(m_value._0),
                                         motor_checked_numcast< u32 >(m_value._1),
                                         motor_checked_numcast< u32 >(m_value._2)});
    else if(motor_type< knl::biguint3 >().isA(expectedType))
        result = Meta::Value(knl::biguint3 {motor_checked_numcast< u64 >(m_value._0),
                                            motor_checked_numcast< u64 >(m_value._1),
                                            motor_checked_numcast< u64 >(m_value._2)});
    else
        motor_notreached();
}

void Int3::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
