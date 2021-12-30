/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/archetypestorage.meta.hh>

#include <motor/world/component/component.meta.hh>
#include <runtime/componentregistry.meta.hh>

#include <motor/introspect/node/array.hh>
#include <motor/introspect/node/object.hh>
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
    minitl::vector< raw< const Meta::Class > > classes;
    minitl::vector< raw< const Meta::Class > > errors;
    bool                                       verify;

    Visitor() : classes(Arena::meta()), errors(Arena::meta()), verify(false)
    {
    }

    using Meta::AST::Node::Visitor::accept;
    void accept(weak< const Meta::AST::Parameter > parameter, istring name,
                weak< const Meta::AST::Node > value) override
    {
        motor_forceuse(parameter);
        motor_forceuse(name);
        value->visit(*this);
    }

    void accept(weak< const Meta::AST::Array >                         arrayNode,
                const minitl::vector< weak< const Meta::AST::Node > >& arrayValue) override
    {
        motor_forceuse(arrayNode);
        for(minitl::vector< weak< const Meta::AST::Node > >::const_iterator it = arrayValue.begin();
            it != arrayValue.end(); ++it)
            (*it)->visit(*this);
    }

    void accept(weak< const Meta::AST::Reference > reference,
                const Meta::Value&                 referencedValue) override
    {
        motor_forceuse(reference);
        raw< const Meta::Class > cls = referencedValue.as< raw< const Meta::Class > >();
        if(!verify)
            classes.push_back(cls);
        else
        {
            bool found = false;
            for(minitl::vector< raw< const Meta::Class > >::const_iterator it = classes.begin();
                it != classes.end(); ++it)
            {
                if(cls == *it)
                {
                    found = true;
                    break;
                }
            }
            if(!found) errors.push_back(cls);
        }
    }
};

class IntrospectionHint : public Meta::AST::IntrospectionHint
{
private:
    minitl::array< raw< const Meta::Class > > m_parameters;

public:
    IntrospectionHint(weak< const Meta::AST::Object > owner, raw< const Meta::Method > method,
                      const Meta::CallInfo& callInfo, u32 argumentThis,
                      const minitl::vector< raw< const Meta::Class > >& parameters)
        : Meta::AST::IntrospectionHint(owner, method, callInfo, argumentThis)
        , m_parameters(Arena::meta(), parameters.begin(), parameters.end())
    {
    }

    virtual bool getPropertyType(Meta::AST::DbContext& context, const istring propertyName,
                                 Meta::Type& propertyType) const override
    {
        bool result
            = Meta::AST::IntrospectionHint::getPropertyType(context, propertyName, propertyType);

        if(!result)
        {
            Meta::Type type = motor_type< ref< KernelScheduler::IProduct > >();
            for(minitl::array< raw< const Meta::Class > >::const_iterator it = m_parameters.begin();
                it != m_parameters.end(); ++it)
            {
                if(propertyName == (*it)->name)
                {
                    type.metaclass = findProductType(*it);
                    propertyType   = type;
                    return true;
                }
            }
        }

        return result;
    }

    virtual bool getPropertyValue(Meta::Value& value, const istring& propertyName,
                                  Meta::Value& result) const override
    {
        bool found = Meta::AST::IntrospectionHint::getPropertyValue(value, propertyName, result);

        if(!found)
        {
            weak< ArchetypeStorage > storage = value.as< weak< ArchetypeStorage > >();
            u32                      i       = 0;
            for(minitl::array< raw< const Meta::Class > >::const_iterator it = m_parameters.begin();
                it != m_parameters.end(); ++it, ++i)
            {
                if(propertyName == (*it)->name)
                {
                    result = Meta::Value(storage->getProduct(i));
                    found  = true;
                    break;
                }
            }
        }

        return found;
    }
};

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

static u32
componentCount(const minitl::array< minitl::array< raw< const Meta::Class > > >& archetypes)
{
    u32 result = 0;
    for(minitl::array< minitl::array< raw< const Meta::Class > > >::const_iterator it
        = archetypes.begin();
        it != archetypes.end(); ++it)
        result += it->size();
    return result;
}

ref< Meta::AST::IntrospectionHint > ArchetypeStorage::Policy::verify(
    Meta::AST::DbContext& context, weak< const Meta::AST::Object > object,
    raw< const Meta::Method > method, const Meta::CallInfo& callInfo, u32 argumentThis) const
{
    Visitor visitor;
    object->getParameter("componentClasses")->visit(visitor);
    visitor.verify = true;
    object->getParameter("archetypes")->visit(visitor);
    if(!visitor.errors.empty())
    {
        for(minitl::vector< raw< const Meta::Class > >::const_iterator it = visitor.errors.begin();
            it != visitor.errors.end(); ++it)
        {
            context.error(object,
                          Meta::AST::Message::MessageType(
                              "Archetype member %s is not part of the input component types")
                              | (*it)->name);
        }
        return ref< IntrospectionHint >();
    }
    return ref< IntrospectionHint >::create(Arena::meta(), object, method, callInfo, argumentThis,
                                            visitor.classes);
}

ArchetypeStorage::ArchetypeStorage(
    weak< ComponentRegistry >                                         registry,
    const minitl::array< raw< const Meta::Class > >&                  componentClasses,
    const minitl::array< minitl::array< raw< const Meta::Class > > >& archetypes)
    : m_registry(registry)
    , m_componentClasses(componentClasses)
    , m_components(Arena::game(), componentCount(archetypes) + componentClasses.size())
{
    motor_forceuse(registry);
    motor_forceuse(archetypes);
    minitl::array< ref< KernelScheduler::IProduct > >::iterator product = m_components.begin();
    for(minitl::array< raw< const Meta::Class > >::const_iterator it = m_componentClasses.begin();
        it != m_componentClasses.end(); ++it, ++product)
    {
        *product = createProduct(*it, this);
    }
}

ArchetypeStorage::~ArchetypeStorage()
{
}

ref< ArchetypeStorage::Runtime >
ArchetypeStorage::createRuntime(weak< const KernelScheduler::ProducerLoader > loader) const
{
    weak< ComponentRegistry::Runtime > registryRuntime = m_registry->getRuntime(loader);
    motor_forceuse(registryRuntime);
    ref< Runtime > result
        = ref< Runtime >::create(Arena::game(), loader->startTask(), m_components.size());
    u32 i = 0;
    for(minitl::array< ref< KernelScheduler::IProduct > >::const_iterator it = m_components.begin();
        it != m_components.end(); ++it, ++i)
    {
        result->parameters[i].first  = *it;
        result->parameters[i].second = (*it)->createParameter();
    }
    return result;
}

ref< KernelScheduler::IProduct > ArchetypeStorage::getProduct(u32 index) const
{
    return m_components[index];
}

}}  // namespace Motor::World
