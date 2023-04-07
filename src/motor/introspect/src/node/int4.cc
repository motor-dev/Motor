/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/int4.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Int4::Int4(knl::bigint4 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Int4::~Int4()
{
}

ConversionCost Int4::distance(const Type& type) const
{
    return ConversionCalculator< knl::bigint4 >::calculate(type);
}

void Int4::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< knl::byte4 >().isA(expectedType))
        result = Meta::Value(knl::byte4 {
            motor_checked_numcast< i8 >(m_value._0), motor_checked_numcast< i8 >(m_value._1),
            motor_checked_numcast< i8 >(m_value._2), motor_checked_numcast< i8 >(m_value._3)});
    else if(motor_type< knl::short4 >().isA(expectedType))
        result = Meta::Value(knl::short4 {
            motor_checked_numcast< i16 >(m_value._0), motor_checked_numcast< i16 >(m_value._1),
            motor_checked_numcast< i16 >(m_value._2), motor_checked_numcast< i16 >(m_value._3)});
    else if(motor_type< knl::int4 >().isA(expectedType))
        result = Meta::Value(knl::int4 {
            motor_checked_numcast< i32 >(m_value._0), motor_checked_numcast< i32 >(m_value._1),
            motor_checked_numcast< i32 >(m_value._2), motor_checked_numcast< i32 >(m_value._3)});
    else if(motor_type< knl::bigint4 >().isA(expectedType))
        result = Meta::Value(knl::bigint4 {
            motor_checked_numcast< i64 >(m_value._0), motor_checked_numcast< i64 >(m_value._1),
            motor_checked_numcast< i64 >(m_value._2), motor_checked_numcast< i64 >(m_value._3)});
    else if(motor_type< knl::ubyte4 >().isA(expectedType))
        result = Meta::Value(knl::ubyte4 {
            motor_checked_numcast< u8 >(m_value._0), motor_checked_numcast< u8 >(m_value._1),
            motor_checked_numcast< u8 >(m_value._2), motor_checked_numcast< u8 >(m_value._3)});
    else if(motor_type< knl::ushort4 >().isA(expectedType))
        result = Meta::Value(knl::ushort4 {
            motor_checked_numcast< u16 >(m_value._0), motor_checked_numcast< u16 >(m_value._1),
            motor_checked_numcast< u16 >(m_value._2), motor_checked_numcast< u16 >(m_value._3)});
    else if(motor_type< knl::uint4 >().isA(expectedType))
        result = Meta::Value(knl::uint4 {
            motor_checked_numcast< u32 >(m_value._0), motor_checked_numcast< u32 >(m_value._1),
            motor_checked_numcast< u32 >(m_value._2), motor_checked_numcast< u32 >(m_value._3)});
    else if(motor_type< knl::biguint4 >().isA(expectedType))
        result = Meta::Value(knl::biguint4 {
            motor_checked_numcast< u64 >(m_value._0), motor_checked_numcast< u64 >(m_value._1),
            motor_checked_numcast< u64 >(m_value._2), motor_checked_numcast< u64 >(m_value._3)});
    else
        motor_notreached();
}

void Int4::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
