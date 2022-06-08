/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/array.hh>
#include <motor/introspect/node/bool.hh>
#include <motor/introspect/node/filename.hh>
#include <motor/introspect/node/float.hh>
#include <motor/introspect/node/float2.hh>
#include <motor/introspect/node/float3.hh>
#include <motor/introspect/node/float4.hh>
#include <motor/introspect/node/int2.hh>
#include <motor/introspect/node/int3.hh>
#include <motor/introspect/node/int4.hh>
#include <motor/introspect/node/integer.hh>
#include <motor/introspect/node/object.hh>
#include <motor/introspect/node/parameter.hh>
#include <motor/introspect/node/reference.hh>
#include <motor/introspect/node/string.hh>

namespace Motor { namespace Meta { namespace AST {

static const Value s_notFound = Value();

void Node::Visitor::accept(weak< const Array >                         arrayNode,
                           const minitl::vector< weak< const Node > >& arrayValue)
{
    motor_forceuse(arrayNode);
    motor_forceuse(arrayValue);
}

void Node::Visitor::accept(weak< const Bool > boolValue)
{
    motor_forceuse(boolValue);
}

void Node::Visitor::accept(weak< const FileName > filenameValue)
{
    motor_forceuse(filenameValue);
}

void Node::Visitor::accept(weak< const Float > floatValue)
{
    motor_forceuse(floatValue);
}

void Node::Visitor::accept(weak< const Float2 > float2Value)
{
    motor_forceuse(float2Value);
}

void Node::Visitor::accept(weak< const Float3 > float3Value)
{
    motor_forceuse(float3Value);
}

void Node::Visitor::accept(weak< const Float4 > float4Value)
{
    motor_forceuse(float4Value);
}

void Node::Visitor::accept(weak< const Integer > integerValue)
{
    motor_forceuse(integerValue);
}

void Node::Visitor::accept(weak< const Int2 > int2Value)
{
    motor_forceuse(int2Value);
}

void Node::Visitor::accept(weak< const Int3 > int3Value)
{
    motor_forceuse(int3Value);
}

void Node::Visitor::accept(weak< const Int4 > int4Value)
{
    motor_forceuse(int4Value);
}

void Node::Visitor::accept(weak< const Object > objectValue)
{
    motor_forceuse(objectValue);
}

void Node::Visitor::accept(weak< const Parameter > parameter, istring name,
                           weak< const Node > value)
{
    motor_forceuse(parameter);
    motor_forceuse(name);
    motor_forceuse(value);
}

void Node::Visitor::accept(weak< const Property > propertyValue)
{
    motor_forceuse(propertyValue);
}

void Node::Visitor::accept(weak< const Reference > referenceValue, const Value& resolvedValue)
{
    motor_forceuse(referenceValue);
    motor_forceuse(resolvedValue);
}

void Node::Visitor::accept(weak< const Reference > referenceValue, weak< const Node > resolvedNode)
{
    motor_forceuse(referenceValue);
    motor_forceuse(resolvedNode);
}

void Node::Visitor::accept(weak< const String > stringValue)
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
        context.error(this, Message::MessageType("circular reference detected"));
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

const Value& Node::getMetadata(const istring name) const
{
    for(minitl::vector< minitl::tuple< const istring, Value > >::const_iterator it
        = m_metadata.begin();
        it != m_metadata.end(); ++it)
    {
        if(it->first == name) return it->second;
    }
    return s_notFound;
}

minitl::tuple< raw< const Meta::Method >, bool > Node::getCall(DbContext& context) const
{
    motor_forceuse(context);
    return minitl::make_tuple(raw< const Meta::Method >::null(), false);
}

ref< Node > Node::getProperty(DbContext& context, const inamespace& name) const
{
    motor_forceuse(name);
    context.error(this, Message::MessageType("object does not have properties"));
    return ref< Node >();
}

void Node::visit(Node::Visitor& visitor) const
{
    motor_assert(m_state >= Resolved, "node is visited but has not yet been resolved");
    doVisit(visitor);
}

}}}  // namespace Motor::Meta::AST
