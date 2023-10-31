/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/archetypestorage.meta.hh>

#include <motor/world/componentregistry.meta.hh>

#include <motor/introspect/node/array.hh>
#include <motor/introspect/node/object.hh>
#include <motor/introspect/node/parameter.hh>
#include <motor/introspect/node/reference.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <utility>

namespace Motor { namespace World {

static raw< const Meta::Class > findProductType(raw< const Meta::Class > componentType)
{
    raw< const Meta::Class > parameterClass
        = KernelScheduler::ISegments::getParameter(componentType);
    if(parameterClass)
    {
        raw< const Meta::Object > productClass = parameterClass->getStaticProperty(
            KernelScheduler::IParameter::getProductTypePropertyName());
        if(productClass)
        {
            return productClass->value.as< raw< const Meta::Class > >();
        }
        else
        {
            motor_error_format(Log::world(), "class {0} has not registered a {1}",
                               parameterClass->name,
                               KernelScheduler::IParameter::getProductTypePropertyName());
            return motor_class< KernelScheduler::IProduct >();
        }
    }
    else
    {
        motor_error_format(Log::world(),
                           "class {0} has not been registered as a segments parameter",
                           componentType->name);
        return motor_class< KernelScheduler::IProduct >();
    }
}

struct Visitor : public Meta::AST::Node::Visitor
{
    weak< const Meta::AST::Node >              owner;
    Meta::AST::DbContext&                      context;
    minitl::vector< raw< const Meta::Class > > classes;
    u32                                        index;
    u32                                        errorCount;
    bool                                       verify;

    Visitor(const weak< const Meta::AST::Node >& owner, Meta::AST::DbContext& context)
        : owner(owner)
        , context(context)
        , classes(Arena::meta())
        , index(0)
        , errorCount(0)
        , verify(false)
    {
    }

    ~Visitor() noexcept override;

    using Meta::AST::Node::Visitor::accept;
    void accept(const weak< const Meta::AST::Parameter >& parameter, istring name,
                const weak< const Meta::AST::Node >& value) override
    {
        motor_forceuse(parameter);
        motor_forceuse(name);
        value->visit(*this);
    }

    void accept(const weak< const Meta::AST::Array >&                  arrayNode,
                const minitl::vector< weak< const Meta::AST::Node > >& arrayValue) override
    {
        motor_forceuse(arrayNode);
        classes.resize(arrayValue.size());
        index = 0;
        for(minitl::vector< weak< const Meta::AST::Node > >::const_iterator it = arrayValue.begin();
            it != arrayValue.end(); ++it, ++index)
        {
            (*it)->visit(*this);
        }
    }

    void accept(const weak< const Meta::AST::Reference >& reference,
                const Meta::Value&                        referencedValue) override
    {
        motor_forceuse(reference);
        auto cls = referencedValue.as< raw< const Meta::Class > >();
        if(!verify)
        {
            for(u32 i = 0; i < index; ++i)
            {
                if(classes[i] == cls)
                {
                    context.error(
                        owner,
                        minitl::format< 512 >(
                            FMT("Component {0} specified at index {1}, duplicate at index {2}"),
                            cls->name, i, index));
                    errorCount++;
                }
            }
            classes[index] = cls;
        }
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
            if(!found)
            {
                context.error(
                    owner, minitl::format< 512 >(
                               FMT("Archetype member {0} is not part of the input component types"),
                               cls->name));
                errorCount++;
            }
        }
    }
};

Visitor::~Visitor() noexcept  // NOLINT
{
}

class IntrospectionHint : public Meta::AST::IntrospectionHint
{
private:
    minitl::vector< raw< const Meta::Class > > m_parameters;

public:
    IntrospectionHint(const weak< const Meta::AST::Object >& owner,
                      raw< const Meta::Method > method, const Meta::CallInfo& callInfo,
                      u32                                               argumentThis,
                      const minitl::vector< raw< const Meta::Class > >& parameters)
        : Meta::AST::IntrospectionHint(owner, method, callInfo, argumentThis)
        , m_parameters(Arena::meta(), parameters.begin(), parameters.end())
    {
    }

    bool getPropertyType(Meta::AST::DbContext& context, const istring propertyName,
                         Meta::Type& propertyType) const override
    {
        bool result
            = Meta::AST::IntrospectionHint::getPropertyType(context, propertyName, propertyType);

        if(!result)
        {
            Meta::Type type = motor_type< ref< KernelScheduler::IProduct > >();
            for(auto m_parameter: m_parameters)
            {
                if(propertyName == m_parameter->name)
                {
                    type.metaclass = findProductType(m_parameter);
                    propertyType   = type;
                    return true;
                }
            }
        }

        return result;
    }

    bool getPropertyValue(Meta::Value& value, const istring& propertyName,
                          Meta::Value& result) const override
    {
        bool found = Meta::AST::IntrospectionHint::getPropertyValue(value, propertyName, result);

        if(!found)
        {
            auto storage = value.as< weak< ArchetypeStorage > >();
            u32  i       = 0;
            for(minitl::vector< raw< const Meta::Class > >::const_iterator it
                = m_parameters.begin();
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
createProduct(raw< const Meta::Class >                       componentClass,
              const weak< const KernelScheduler::Producer >& producer)
{
    raw< const Meta::Class > productClass = findProductType(componentClass);
    if(!productClass)
    {
        return {};
    }
    motor_assert_format(productClass->constructor, "product class {0} does not have a constructor",
                        productClass->name);
    motor_assert_format(productClass->constructor->overloads.size() == 1,
                        "product class {0} has more than one constructor overload",
                        productClass->name);
    Meta::Value                   parameter(producer);
    const Meta::Method::Overload& overload = productClass->constructor->overloads[0];
    return (overload.call)(productClass->constructor, &parameter, 1)
        .as< ref< KernelScheduler::IProduct > >();
}

static u32
componentCount(const minitl::vector< minitl::vector< raw< const Meta::Class > > >& archetypes)
{
    u32 result = 0;
    for(const auto& archetype: archetypes)
        result += u32(archetype.size());
    return result;
}

ref< Meta::AST::IntrospectionHint > ArchetypeStorage::Policy::verify(
    Meta::AST::DbContext& context, weak< const Meta::AST::Object > object,
    raw< const Meta::Method > method, const Meta::CallInfo& callInfo, u32 argumentThis) const
{
    Visitor visitor(object, context);
    object->getParameter(istring("componentClasses"))->visit(visitor);
    visitor.verify = true;
    object->getParameter(istring("archetypes"))->visit(visitor);
    if(visitor.errorCount)
        return ref< IntrospectionHint >();
    else
        return ref< IntrospectionHint >::create(Arena::meta(), object, method, callInfo,
                                                argumentThis, visitor.classes);
}

ArchetypeStorage::ArchetypeStorage(
    const weak< ComponentRegistry >&                                    registry,
    minitl::vector< raw< const Meta::Class > >                          componentClasses,
    const minitl::vector< minitl::vector< raw< const Meta::Class > > >& archetypes)
    : m_registry(registry)
    , m_componentClasses(std::move(componentClasses))
    , m_components(Arena::game(), componentCount(archetypes) + componentClasses.size())
{
    motor_forceuse(registry);
    motor_forceuse(archetypes);
    minitl::vector< ref< KernelScheduler::IProduct > >::iterator product = m_components.begin();
    for(minitl::vector< raw< const Meta::Class > >::const_iterator it = m_componentClasses.begin();
        it != m_componentClasses.end(); ++it, ++product)
    {
        *product = createProduct(*it, this);
    }
}

ArchetypeStorage::~ArchetypeStorage() = default;

ref< ArchetypeStorage::Runtime >
ArchetypeStorage::createRuntime(weak< const KernelScheduler::ProducerLoader > loader) const
{
    weak< ComponentRegistry::Runtime > registryRuntime = m_registry->getRuntime(loader);
    motor_forceuse(registryRuntime);
    ref< Runtime > result
        = ref< Runtime >::create(Arena::game(), loader->startTask(), u32(m_components.size()));
    u32 i = 0;
    for(minitl::vector< ref< KernelScheduler::IProduct > >::const_iterator it
        = m_components.begin();
        it != m_components.end(); ++it, ++i)
    {
        result->parameters[i].first = *it;
        if(*it) result->parameters[i].second = (*it)->createParameter();
    }
    return result;
}

ref< KernelScheduler::IProduct > ArchetypeStorage::getProduct(u32 index) const
{
    return m_components[index];
}

}}  // namespace Motor::World
