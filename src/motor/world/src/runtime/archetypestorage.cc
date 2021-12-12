/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/archetypestorage.meta.hh>

#include <motor/world/component/component.meta.hh>

#include <motor/introspect/node/parameter.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>
#include <motor/scheduler/kernel/parameters/segments.hh>
#include <motor/scheduler/kernel/producerloader.hh>

namespace Motor { namespace World {

static raw< const Meta::Class > findProductType(raw< const Meta::Class > componentType)
{
    raw< const Meta::Class > parameterClass
        = KernelScheduler::ISegments::getParameter(componentType);
    if(parameterClass)
    {
        raw< const Meta::ObjectInfo > productClass = parameterClass->getStaticProperty(
            KernelScheduler::IParameter::getProductTypePropertyName());
        if(productClass)
        {
            return productClass->value.as< raw< const Meta::Class > >();
        }
        else
        {
            motor_error("class %s has not registered a %s" | parameterClass->name
                        | KernelScheduler::IParameter::getProductTypePropertyName());
            return motor_class< KernelScheduler::IProduct >();
        }
    }
    else
    {
        motor_error("class %s has not been registered as a segments parameter"
                    | componentType->fullname());
        return motor_class< KernelScheduler::IProduct >();
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
        result.metaclass = findProductType(referencedValue.as< raw< const Meta::Class > >());
    }
};

ArchetypeStorage::IntrospectionHint::IntrospectionHint(weak< const Meta::AST::Object > owner,
                                                       raw< const Meta::Method >       method,
                                                       const Meta::CallInfo&           callInfo,
                                                       u32                             argumentThis)
    : Meta::AST::IntrospectionHint(owner, method, callInfo, argumentThis)
{
}

bool ArchetypeStorage::IntrospectionHint::getPropertyType(Meta::AST::DbContext& context,
                                                          const istring         propertyName,
                                                          Meta::Type&           propertyType) const
{
    static const istring componentPropertyName("component");
    bool                 result
        = Meta::AST::IntrospectionHint::getPropertyType(context, propertyName, propertyType);

    if(result && propertyName == componentPropertyName)
    {
        weak< const Meta::AST::Parameter > parameter = m_owner->getParameter("componentClass");
        motor_assert(parameter, "could not locate parameter componentClass");
        Visitor visitor;
        parameter->visit(visitor);
        propertyType = visitor.result;
    }

    return result;
}

static ref< KernelScheduler::IProduct >
createProduct(raw< const Meta::Class >                componentClass,
              weak< const KernelScheduler::Producer > producer)
{
    raw< const Meta::Class > productClass = findProductType(componentClass);
    if(!productClass)
    {
        return ref< KernelScheduler::IProduct >();
    }
    motor_assert(productClass->constructor,
                 "product class %s does not have a constructor" | productClass->fullname());
    motor_assert(productClass->constructor->overloads.count == 1,
                 "product class %s has more than one constructor overload"
                     | productClass->fullname());
    Meta::Value                   parameter(producer);
    const Meta::Method::Overload& overload = productClass->constructor->overloads[0];
    return (overload.call)(productClass->constructor, &parameter, 1)
        .as< ref< KernelScheduler::IProduct > >();
}

ArchetypeStorage::ArchetypeStorage(raw< const Meta::Class > componentClass)
    : m_componentClass(componentClass)
    , component(createProduct(m_componentClass, this))
{
}

ArchetypeStorage::~ArchetypeStorage()
{
}

ref< ArchetypeStorage::Runtime >
ArchetypeStorage::createRuntime(weak< const KernelScheduler::ProducerLoader > loader) const
{
    ref< Runtime > result        = ref< Runtime >::create(Arena::game(), loader->startTask(), 1);
    result->parameters[0].first  = component;
    result->parameters[0].second = component->createParameter();
    return result;
}

}}  // namespace Motor::World
