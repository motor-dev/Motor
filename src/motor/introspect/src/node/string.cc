/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/string.hh>
#include <motor/meta/interfacetable.hh>

namespace Motor { namespace Meta { namespace AST {

String::String(const char* value) : Node(), m_value(Arena::script().strdup(value))
{
}

String::~String() = default;

ConversionCost String::distance(const Type& type) const
{
    if(type.metaclass->interfaces->charpInterface)
    {
        return type.metaclass->interfaces->charpInterface->valueType.calculateConversionTo(type);
    }
    else
    {
        return ConversionCost::s_incompatible;
    }
}

void String::doEval(const Meta::Type& expectedType, Value& result) const
{
    result = (*expectedType.metaclass->interfaces->charpInterface->construct)(m_value);
}

void String::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
