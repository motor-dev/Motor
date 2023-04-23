/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/float3.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Float3::Float3(knl::float3 value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Float3::~Float3() = default;

ConversionCost Float3::distance(const Type& type) const
{
    return ConversionCalculator< knl::float3 >::calculate(type);
}

void Float3::doEval(const Meta::Type& expectedType, Meta::Value& result) const
{
    motor_forceuse(expectedType);
    result = Meta::Value(m_value);
}

void Float3::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
