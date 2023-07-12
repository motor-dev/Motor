/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/introspectionhint.meta.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/introspect/node/object.hh>
#include <motor/meta/call.hh>
#include <motor/meta/operatortable.hh>
#include <motor/meta/property.meta.hh>

namespace Motor { namespace Meta { namespace AST {

IntrospectionHint::IntrospectionHint(const weak< const Object >& owner, raw< const Method > method,
                                     const CallInfo& callInfo, u32 argumentThis)
    : m_owner(owner)
    , m_method(method)
    , m_callInfo(callInfo)
    , m_argumentThis(argumentThis)
{
}

IntrospectionHint::~IntrospectionHint() = default;

ConversionCost IntrospectionHint::calculateConversionTo(const Type& targetType) const
{
    return m_callInfo.overload->returnType.calculateConversionTo(targetType);
}

Value IntrospectionHint::call(const ArgInfo parameters[], u32 argumentCount) const
{
    return Meta::call< weak< const Node > >(
        m_method, m_callInfo, {parameters, parameters + m_argumentThis},
        {parameters + m_argumentThis, parameters + argumentCount});
}

minitl::raw< const Method > IntrospectionHint::getCall(DbContext& context) const
{
    raw< const Class > cls = m_callInfo.overload->returnType.metaclass;
    if(cls->operators->call)
    {
        return cls->operators->call;
    }
    if(cls->operators->dynamicCall)
        context.error(m_owner, minitl::format< 512 >(FMT("call on object of type {0} is dynamic"),
                                                     m_callInfo.overload->returnType));
    return {};
}

Type IntrospectionHint::getType() const
{
    return m_callInfo.overload->returnType;
}

bool IntrospectionHint::getPropertyValue(Value& value, const istring& propertyName,
                                         Value& result) const
{
    bool found;
    result = value.type().metaclass->get(value, propertyName, found);
    return found;
}
bool IntrospectionHint::getPropertyType(DbContext& context, istring name, Type& propertyType) const
{
    motor_forceuse(context);
    const Type&                 type     = m_callInfo.overload->returnType;
    raw< const Meta::Property > property = type.metaclass->getProperty(name);
    if(property)
    {
        propertyType = property->type;
        return true;
    }
    else
    {
        return false;
    }
}

}}}  // namespace Motor::Meta::AST
