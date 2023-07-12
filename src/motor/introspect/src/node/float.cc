/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/float.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

Float::Float(float value) : Node(), m_value(value)
{
    motor_forceuse(m_value);
}

Float::~Float() = default;

ConversionCost Float::distance(const Type& type) const
{
    return motor_type< double >().calculateConversionTo(type);
}

void Float::doEval(const Meta::Type& expectedType, Meta::Value& result) const
{
    if(motor_type< float >().isA(expectedType))
        result = Meta::Value((float)m_value);
    else
        result = Meta::Value((double)m_value);
}

void Float::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
