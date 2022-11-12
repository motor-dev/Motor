/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/float4.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Float4::Float4(knl::float4 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Float4::~Float4()
{
}

ConversionCost Float4::distance(const Type& type) const
{
    return ConversionCalculator< knl::float4 >::calculate(type);
}

void Float4::doEval(const Meta::Type& expectedType, Meta::Value& result) const
{
    motor_forceuse(expectedType);
    result = Meta::Value(m_value);
}

void Float4::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
