/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/property.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>

namespace Motor { namespace Meta { namespace AST {

Property::Property(ref< const Object > owner, const inamespace& propertyName)
    : Node()
    , m_owner(owner)
    , m_propertyName(propertyName)
    , m_type()
{
}

Property::~Property()
{
}

ConversionCost Property::distance(const Type& type) const
{
    return m_type.calculateConversion(type);
}

minitl::tuple< raw< const Meta::Method >, bool > Property::getCall(DbContext& context) const
{
    motor_forceuse(context);
    return minitl::make_tuple(raw< const Method >::null(), false);
}

bool Property::doResolve(DbContext& context)
{
    if(!m_owner->getPropertyType(context, m_propertyName[0], m_type))
    {
        context.error(this, minitl::format< 512 >(FMT("type {0} does not have a member {1}"),
                                                  m_owner->getType().name(), m_propertyName[0]));
    }
    for(u32 i = 1; i < m_propertyName.size(); ++i)
    {
        raw< const Meta::Property > property = m_type.metaclass->getProperty(m_propertyName[i]);
        if(property)
        {
            m_type = property->type;
        }
        else
        {
            context.error(this, minitl::format< 512 >(FMT("type {0} does not have a member {1}"),
                                                      m_type.name(), m_propertyName[i]));
            return false;
        }
    }
    return true;
}

void Property::doEval(const Type& expectedType, Value& result) const
{
    motor_forceuse(expectedType);
    result = m_owner->eval(expectedType);
    Value temp;
    bool  found = m_owner->getPropertyValue(result, m_propertyName[0], temp);
    motor_assert_format(found, "type {0} does not have a property {1}", result.type().name(),
                        m_propertyName[0]);
    result.swap(temp);
    for(u32 i = 1; i < m_propertyName.size(); ++i)
    {
        Value v = result.type().metaclass->get(result, m_propertyName[i], found);
        motor_assert_format(found, "type {0} does not have a property {1}", result.type().name(),
                            m_propertyName[i]);
        result.swap(v);
    }
    /* TODO: Policy */
    Value v(expectedType, result);
    result.swap(v);
}

void Property::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
