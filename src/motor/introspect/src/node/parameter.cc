/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/parameter.hh>

namespace Motor { namespace Meta { namespace AST {

Parameter::Parameter(istring name, const ref< Node >& value) : m_name(name), m_value(value)
{
}

Parameter::~Parameter() = default;

ConversionCost Parameter::distance(const Type& type) const
{
    return m_value->distance(type);
}

bool Parameter::doResolve(DbContext& context)
{
    return m_value->resolve(context);
}

void Parameter::doEval(const Type& expectedType, Value& result) const
{
    return m_value->eval(expectedType, result);
}

void Parameter::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this, m_name, m_value);
}

}}}  // namespace Motor::Meta::AST
