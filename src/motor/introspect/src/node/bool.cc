/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/bool.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Bool::Bool(bool value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Bool::~Bool()
{
}

ConversionCost Bool::distance(const Type& type) const
{
    return ConversionCalculator< bool >::calculate(type);
}

void Bool::doEval(const Meta::Type& expectedType, Value& result) const
{
    motor_forceuse(expectedType);
    result = Meta::Value(m_value);
}

void Bool::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
