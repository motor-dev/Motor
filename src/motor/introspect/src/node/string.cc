/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/string.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

String::String(const char* value) : Node(), m_value(Arena::script().strdup(value))
{
}

String::~String()
{
}

ConversionCost String::distance(const Type& type) const
{
    if(type.metaclass->type() == ClassType_String)
        return ConversionCost();
    else
        return ConversionCost::s_incompatible;
}

void String::doEval(const Meta::Type& expectedType, Value& result) const
{
    if(motor_type< istring >().isA(expectedType))
        result = Meta::Value(istring(m_value));
    else if(motor_type< inamespace >().isA(expectedType))
        result = Meta::Value(inamespace(m_value));
    else
        motor_notreached();
}

void String::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
