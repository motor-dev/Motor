/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/float2.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Float2::Float2(knl::float2 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Float2::~Float2() = default;

ConversionCost Float2::distance(const Type& type) const
{
    return ConversionCalculator< knl::float2 >::calculate(type);
}

void Float2::doEval(const Meta::Type& expectedType, Meta::Value& result) const
{
    motor_forceuse(expectedType);
    result = Meta::Value(m_value);
}

void Float2::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
