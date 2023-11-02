/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/array.hh>
#include <motor/introspect/node/bool.hh>
#include <motor/introspect/node/filename.hh>
#include <motor/introspect/node/float.hh>
#include <motor/introspect/node/integer.hh>
#include <motor/introspect/node/object.hh>
#include <motor/introspect/node/parameter.hh>
#include <motor/introspect/node/reference.hh>
#include <motor/introspect/node/string.hh>

namespace Motor { namespace Meta { namespace AST {

static const Value s_notFound = Value();

void Node::Visitor::accept(const weak< const Array >&                  arrayNode,
                           const minitl::vector< weak< const Node > >& arrayValue)
{
    motor_forceuse(arrayNode);
    motor_forceuse(arrayValue);
}

void Node::Visitor::accept(const weak< const Bool >& boolValue)
{
    motor_forceuse(boolValue);
}

void Node::Visitor::accept(const weak< const FileName >& filenameValue)
{
    motor_forceuse(filenameValue);
}

void Node::Visitor::accept(const weak< const Float >& floatValue)
{
    motor_forceuse(floatValue);
}

void Node::Visitor::accept(const weak< const Integer >& integerValue)
{
    motor_forceuse(integerValue);
}

void Node::Visitor::accept(const weak< const Object >& objectValue)
{
    motor_forceuse(objectValue);
}

void Node::Visitor::accept(const weak< const Parameter >& parameter, istring name,
                           const weak< const Node >& value)
{
    motor_forceuse(parameter);
    motor_forceuse(name);
    motor_forceuse(value);
}

void Node::Visitor::accept(const weak< const Property >& propertyValue)
{
    motor_forceuse(propertyValue);
}

void Node::Visitor::accept(const weak< const Reference >& referenceValue,
                           const Value&                   referencedValue)
{
    motor_forceuse(referenceValue);
    motor_forceuse(referencedValue);
}

void Node::Visitor::accept(const weak< const Reference >& referenceValue,
                           const weak< const Node >&      referencedNode)
{
    motor_forceuse(referenceValue);
    motor_forceuse(referencedNode);
}

void Node::Visitor::accept(const weak< const String >& stringValue)
{
    motor_forceuse(stringValue);
}

bool Node::doResolve(DbContext& context)
{
    motor_forceuse(context);
    return true;
}

bool Node::resolve(DbContext& context)
{
    motor_assert(m_state != Evaluated, "node is already evaluated");
    if(m_state == InResolution)
    {
        context.error(this, minitl::format_buffer< 512 > {"circular reference detected"});
        return false;
    }
    else if(m_state == Resolved)
        return true;
    else if(m_state == ResolvedError)
        return false;
    else
    {
        m_state     = InResolution;
        bool result = doResolve(context);
        m_state     = result ? Resolved : ResolvedError;
        return result;
    }
}

void Node::eval(const Type& expectedType, Value& result) const
{
    if(m_state != Evaluated)
    {
        motor_assert(m_state == Resolved, "node has skipped resolution stage");
        doEval(expectedType, result);
        m_cache = Value(Value::ByRef(result));
        m_state = Evaluated;
    }
    else
    {
        result = m_cache;
    }
}

Value Node::eval(const Type& expectedType) const
{
    if(m_state != Evaluated)
    {
        motor_assert(m_state == Resolved, "node has skipped resolution stage");
        doEval(expectedType, m_cache);
        m_state = Evaluated;
    }
    return Value(Value::ByRef(m_cache));
}

const Value& Node::getMetadata(istring name) const
{
    for(const auto& it: m_metadata)
    {
        if(it.first == name) return it.second;
    }
    return s_notFound;
}

raw< const Meta::Method > Node::getCall(DbContext& context) const
{
    motor_forceuse(context);
    return {};
}

ref< Node > Node::getProperty(DbContext& context, const inamespace& name) const
{
    motor_forceuse(name);
    context.error(this, minitl::format_buffer< 512 > {"object does not have properties"});
    return {};
}

void Node::visit(Node::Visitor& visitor) const
{
    motor_assert(m_state >= Resolved, "node is visited but has not yet been resolved");
    doVisit(visitor);
}

}}}  // namespace Motor::Meta::AST
