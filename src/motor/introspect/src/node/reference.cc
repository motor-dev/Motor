/* Motor <motor.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/reference.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/object.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/operatortable.hh>

namespace Motor { namespace Meta { namespace AST {

Reference::Reference(const inamespace& name) : Node(), m_referenceName(name)
{
}

Reference::~Reference() = default;

bool Reference::doResolve(DbContext& context)
{
    weak< const Namespace > ns         = context.rootNamespace;
    inamespace              properties = m_referenceName;
    inamespace              current;
    while(properties.size())
    {
        istring                 n     = properties[0];
        weak< const Namespace > child = ns->getChild(n);
        if(child)
        {
            ns = child;
            properties.pop_front();
            if(properties.size() == 0) m_value = Value(Value::ByRef(ns->getValue()));
        }
        else
        {
            ref< Node > node = ns->getNode(n);
            if(node)
            {
                if(node->resolve(context))
                {
                    m_node = node;
                    properties.pop_front();
                    if(properties.size() != 0)
                    {
                        ref< Node > propertyNode = m_node->getProperty(context, properties);
                        if(propertyNode) propertyNode->resolve(context);
                        m_node = propertyNode;
                    }
                    break;
                }
                else
                {
                    return false;
                }
            }
            else
            {
                const Value& v = ns->getValue();
                if(!v)
                {
                    context.error(this,
                                  minitl::format< 512 >(FMT("when resolving {0}: namespace {1} "
                                                            "does not have a child named {2}"),
                                                        m_referenceName, current, n));
                    return false;
                }
                else
                {
                    m_value = Value(Value::ByRef(v));
                    while(properties.size())
                    {
                        n = properties.pop_front();
                        bool  found;
                        Type  t         = v.type();
                        Value propValue = t.metaclass->get(m_value, n, found);
                        m_value.swap(propValue);
                        if(!found)
                        {
                            context.error(this, minitl::format< 512 >(
                                                    FMT("when resolving {0}: object {1} of type "
                                                        "{2} does not have a property named {3}"),
                                                    m_referenceName, current, t, n));
                            return false;
                        }
                        current.push_back(n);
                    }
                }
                break;
            }
        }
        current.push_back(n);
    }
    return true;
}

ConversionCost Reference::distance(const Type& type) const
{
    if(m_node)
    {
        return m_node->distance(type);
    }
    else
    {
        return m_value.type().calculateConversionTo(type);
    }
}

void Reference::doEval(const Type& expectedType, Value& result) const
{
    if(m_node)
    {
        m_node->eval(expectedType, result);
    }
    else
    {
        result = m_value;
    }
}

raw< const Meta::Method > Reference::getCall(DbContext& context) const
{
    motor_forceuse(context);
    if(m_node)
    {
        return raw< const Method >::null();
    }
    else
    {
        raw< const Class > metaclass = m_value.type().metaclass;
        if(metaclass->operators->call)
        {
            return metaclass->operators->call;
        }
        else if(metaclass->operators->dynamicCall)
        {
            return (*metaclass->operators->dynamicCall)(m_value);
        }
        else
        {
            return raw< const Method >::null();
        }
    }
}

void Reference::doVisit(Node::Visitor& visitor) const
{
    if(m_node)
        visitor.accept(this, m_node);
    else
        visitor.accept(this, m_value);
}

}}}  // namespace Motor::Meta::AST
