/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/string.hh>
#include <motor/meta/operatortable.hh>

namespace Motor { namespace Meta { namespace AST {

String::String(const char* value) : Node(), m_value(Arena::script().strdup(value))
{
}

String::~String() = default;

ConversionCost String::distance(const Type& type) const
{
    if(type.metaclass->operators->stringOperators)
    {
        return type.metaclass->operators->stringOperators->valueType.calculateConversionTo(type);
    }
    else
    {
        return ConversionCost::s_incompatible;
    }
}

void String::doEval(const Meta::Type& expectedType, Value& result) const
{
    result = (*expectedType.metaclass->operators->stringOperators->construct)(m_value);
}

void String::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
