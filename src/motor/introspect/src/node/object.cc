/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/object.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/introspect/node/parameter.hh>
#include <motor/introspect/node/property.hh>
#include <motor/introspect/node/reference.hh>
#include <motor/introspect/policy.meta.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/call.hh>
#include <motor/meta/value.hh>
#include <motor/minitl/utility.hh>

namespace Motor { namespace Meta { namespace AST {

Object::Object(const ref< Reference >& className, minitl::vector< ref< Parameter > > parameters)
    : Node()
    , m_className(className)
    , m_parameters(minitl::move(parameters))
    , m_arguments(Arena::temporary())
{
}

Object::~Object() = default;

ConversionCost Object::distance(const Type& type) const
{
    if(m_introspectionHint)
    {
        return m_introspectionHint->calculateConversion(type);
    }
    else
    {
        return ConversionCost::s_incompatible;
    }
}

minitl::tuple< raw< const Meta::Method >, bool > Object::getCall(DbContext& context) const
{
    if(m_introspectionHint)
    {
        return m_introspectionHint->getCall(context);
    }
    else
    {
        return minitl::make_tuple(raw< const Method >::null(), false);
    }
}

bool Object::doResolve(DbContext& context)
{
    motor_assert(!m_introspectionHint,
                 "object has already been resolved; make sure to reset the state first");
    bool result = resolveInternal(context);
    if(result)
    {
        motor_assert(m_introspectionHint, "object resolution succeeded without providing a hint");
    }
    else
    {
        if(motor_assert(!m_introspectionHint, "object resolution failed, but produced a hint"))
            m_introspectionHint.clear();
    }
    return result;
}

bool Object::resolveInternal(DbContext& context)
{
    bool result = m_className->resolve(context);

    for(const auto& m_parameter: m_parameters)
    {
        result &= m_parameter->resolve(context);
    }
    if(result)
    {
        minitl::tuple< raw< const Meta::Method >, bool > method = m_className->getCall(context);
        if(!method.first)
        {
            context.error(
                this, minitl::format< 512 >(FMT("unable to call object {0}"), m_className->name()));
            result = false;
        }
        else
        {
            u32 argumentThis  = method.second ? 1 : 0;
            u32 argumentCount = motor_checked_numcast< u32 >(m_parameters.size()) + argumentThis;
            m_arguments.resize(argumentCount);
            if(method.second)
            {
                m_arguments[0] = IntrospectionHint::ArgInfo(this);
            }
            for(u32 currentArg = 0; currentArg < m_parameters.size(); ++currentArg)
            {
                m_arguments[currentArg + argumentThis] = IntrospectionHint::ArgInfo(
                    m_parameters[currentArg]->name(), m_parameters[currentArg]);
            }

            IntrospectionHint::ArgInfo* arguments
                = m_arguments.empty() ? nullptr : &m_arguments.front();
            CallInfo callInfo
                = Meta::resolve(method.first, {arguments, arguments + argumentThis},
                                {arguments + argumentThis, arguments + argumentCount});
            if(callInfo.overload)
            {
                Meta::Value policyTag = callInfo.overload->getTag(motor_class< Policy >());
                if(policyTag)
                {
                    const auto& policy     = policyTag.as< const Policy& >();
                    u32         errorCount = context.errorCount;
                    m_introspectionHint
                        = policy.verify(context, this, method.first, callInfo, argumentThis);
                    result = errorCount == context.errorCount;
                }
                else
                {
                    m_introspectionHint = ref< IntrospectionHint >::create(
                        Arena::meta(), this, method.first, callInfo, argumentThis);
                }
            }
            else
            {
                result = false;
                context.error(
                    this,
                    minitl::format< 512 >(
                        FMT("unable to call object {0}: no overload could convert all arguments"),
                        m_className->name()));
            }
        }
    }
    return result;
}

void Object::doEval(const Type& expectedType, Value& result) const
{
    motor_forceuse(expectedType);
    const IntrospectionHint::ArgInfo* arguments
        = m_arguments.empty() ? nullptr : &m_arguments.front();
    result = m_introspectionHint->call(arguments, motor_checked_numcast< u32 >(m_arguments.size()));
}

Type Object::getType() const
{
    return m_introspectionHint->getType();
}

bool Object::getPropertyValue(Value& value, istring propertyName, Value& result) const
{
    return m_introspectionHint->getPropertyValue(value, propertyName, result);
}

bool Object::getPropertyType(DbContext& context, istring propertyName, Type& propertyType) const
{
    return m_introspectionHint->getPropertyType(context, propertyName, propertyType);
}

ref< Node > Object::getProperty(DbContext& context, const inamespace& propertyName) const
{
    motor_forceuse(context);
    return ref< Property >::create(Arena::general(), ref_from_this< Object >(), propertyName);
}

weak< const Parameter > Object::getParameter(istring parameterName) const
{
    for(const auto& m_parameter: m_parameters)
    {
        if(m_parameter->name() == parameterName) return m_parameter;
    }
    return {};
}

void Object::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
