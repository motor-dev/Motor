
/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/component/logiccomponentstorage.meta.hh>

#include <motor/introspect/node/object.hh>
#include <motor/introspect/node/parameter.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

namespace Motor { namespace World { namespace Component {

static Meta::Type findProductType(raw< const Meta::Class > componentType)
{
    istring parameterName(minitl::format< 256u >("Segments<%s>") | componentType->name);
    raw< const Meta::Class > parameterClass
        = KernelScheduler::IParameter::getParameterClass(parameterName);
    if(parameterClass)
    {
        raw< const Meta::ObjectInfo > productClass = parameterClass->getStaticProperty(
            KernelScheduler::IParameter::getProductTypePropertyName());
        if(productClass)
        {
            return productClass->value.as< const Meta::Type& >();
        }
        else
        {
            motor_error("class %s has not registered a %s" | parameterClass->name
                        | KernelScheduler::IParameter::getProductTypePropertyName());
            return motor_type< ref< KernelScheduler::IProduct > >();
        }
    }
    else
    {
        motor_error("class %s has not been registered as a parameter type" | parameterName);
        return motor_type< ref< KernelScheduler::IProduct > >();
    }
}

struct Visitor : public Meta::AST::Node::Visitor
{
    Meta::Type result;

    Visitor() : result(motor_type< ref< KernelScheduler::IProduct > >())
    {
    }

    using Meta::AST::Node::Visitor::accept;
    void accept(weak< const Meta::AST::Parameter > parameter, istring name,
                weak< const Meta::AST::Node > value)
    {
        motor_forceuse(parameter);
        motor_forceuse(name);
        value->visit(*this);
    }
    void accept(weak< const Meta::AST::Reference > reference, const Meta::Value& referencedValue)
    {
        motor_forceuse(reference);
        result = findProductType(referencedValue.as< raw< const Meta::Class > >());
    }
};

LogicComponentStorage::IntrospectionHint::IntrospectionHint(weak< const Meta::AST::Object > owner,
                                                            const Meta::CallInfo& callInfo,
                                                            u32                   argumentThis)
    : Meta::AST::IntrospectionHint(owner, callInfo, argumentThis)
{
}

LogicComponentStorage::IntrospectionHint::~IntrospectionHint()
{
}

bool LogicComponentStorage::IntrospectionHint::getPropertyType(Meta::AST::DbContext& context,
                                                               const istring         name,
                                                               Meta::Type& propertyType) const
{
    /* overrides type of "components" property */
    bool result = Meta::AST::IntrospectionHint::getPropertyType(context, name, propertyType);
    if(result && name == istring("components"))
    {
        weak< const Meta::AST::Parameter > parameter = m_owner->getParameter("componentType");
        motor_assert(parameter, "could not locate parameter %s" | name);
        Visitor visitor;
        parameter->visit(visitor);
        propertyType = visitor.result;
    }
    return result;
}

static ref< KernelScheduler::IProduct > makeProduct(raw< const Meta::Class >     componentType,
                                                    weak< StorageConfiguration > configuration)
{
    istring parameterName(minitl::format< 256u >("Segments<%s>") | componentType->name);
    raw< const Meta::Class > parameterClass
        = KernelScheduler::IParameter::getParameterClass(parameterName);
    if(parameterClass)
    {
        ref< KernelScheduler::IParameter > parameter
            = parameterClass->constructor->doCall(0, 0).as< ref< KernelScheduler::IParameter > >();
        return parameter->makeProduct(parameter, configuration->updateStart());
    }
    else
    {
        motor_error("could not locate class %s" | parameterName);
        return ref< KernelScheduler::IProduct >();
    }
}

LogicComponentStorage::LogicComponentStorage(weak< StorageConfiguration > configuration,
                                             raw< const Meta::Class >     componentType)
    : components(makeProduct(componentType, configuration))
{
}

}}}  // namespace Motor::World::Component
