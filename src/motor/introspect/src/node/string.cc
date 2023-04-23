/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/string.hh>

#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

String::String(const char* value) : Node(), m_value(Arena::script().strdup(value))
{
}

String::~String() = default;

ConversionCost String::distance(const Type& type) const
{
    if(type.metaclass->type() == ClassType_String)
        return ConversionCost();
    else
        return ConversionCost::s_incompatible;
}

void String::doEval(const Meta::Type& expectedType, Value& result) const
{
    switch(expectedType.metaclass->index())
    {
    case ClassIndex_istring: result = Meta::Value(istring(m_value)); break;
    case ClassIndex_ifilename: result = Meta::Value(ifilename(m_value)); break;
    case ClassIndex_ipath: result = Meta::Value(ipath(m_value)); break;
    case ClassIndex_inamespace: result = Meta::Value(inamespace(m_value)); break;
    case ClassIndex_text: result = Meta::Value(text(m_value)); break;
    default: motor_notreached();
    }
}

void String::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
