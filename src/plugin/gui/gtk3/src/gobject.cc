/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gobject.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>
#include <meta/constructor.meta.hh>
#include <meta/property.meta.hh>

#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGObjectClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_info_format(Log::gtk(), "finishing registration of type {0}", g_type_name(type));
    auto*        objectClass = static_cast< GObjectClass* >(g_type_class_ref(type));
    guint        paramSpecCount;
    GParamSpec** paramSpecs    = g_object_class_list_properties(objectClass, &paramSpecCount);
    u32          propertyCount = 0;
    u32          constructorParameterCount = 0;
    for(guint i = 0; i < paramSpecCount; ++i)
    {
        if(paramSpecs[i]->value_type == G_TYPE_POINTER
           || paramSpecs[i]->value_type == G_TYPE_VARIANT)
        {
            motor_warning_format(Log::gtk(), "skipping property {0}.{1} of type {2}",
                                 g_type_name(type), g_param_spec_get_name(paramSpecs[i]),
                                 g_type_name(paramSpecs[i]->value_type));
            continue;
        }
        if(paramSpecs[i]->flags & G_PARAM_DEPRECATED)
        {
            motor_debug_format(Log::gtk(), "skipping deprecated property {0}.{1}",
                               g_type_name(type), g_param_spec_get_name(paramSpecs[i]));
            continue;
        }
        if(((paramSpecs[i]->flags & G_PARAM_READWRITE) == G_PARAM_READWRITE)
           || (paramSpecs[i]->flags & G_PARAM_CONSTRUCT))
        {
            constructorParameterCount++;
        }
        if((paramSpecs[i]->flags & G_PARAM_READWRITE)
           && !(paramSpecs[i]->flags & G_PARAM_CONSTRUCT_ONLY))
        {
            propertyCount++;
        }
        if((paramSpecs[i]->flags & G_PARAM_WRITABLE) && !(paramSpecs[i]->flags & G_PARAM_READABLE))
        {
            motor_warning_format(Log::gtk(), "skipping signal property {0}.{1} [{2}]\n    {3}",
                                 g_type_name(type), g_param_spec_get_name(paramSpecs[i]),
                                 g_type_name(paramSpecs[i]->value_type),
                                 g_param_spec_get_blurb(paramSpecs[i]));
        }
    }
    if(G_TYPE_IS_INSTANTIATABLE(type))
    {
        auto*                    constructor = plugin.allocate< Constructor >();
        auto*                    overload    = plugin.allocate< Meta::Method::Overload >();
        Meta::Method::Parameter* parameters  = nullptr;
        raw< const Meta::Class > metaclass   = {cls};
        if(constructorParameterCount)
        {
            parameters = plugin.allocateArray< Meta::Method::Parameter >(constructorParameterCount);
            for(guint i = 0, j = 0; i < paramSpecCount; ++i)
            {
                if(paramSpecs[i]->value_type == G_TYPE_POINTER
                   || paramSpecs[i]->value_type == G_TYPE_VARIANT
                   || (paramSpecs[i]->flags & G_PARAM_DEPRECATED))
                {
                    continue;
                }
                if(((paramSpecs[i]->flags & G_PARAM_READWRITE) == G_PARAM_READWRITE)
                   || (paramSpecs[i]->flags & G_PARAM_CONSTRUCT))
                {
                    auto* defaultValue = plugin.allocate< Meta::Value >();
                    new(defaultValue) Meta::Value(
                        plugin.fromGValue(g_param_spec_get_default_value(paramSpecs[i])));
                    Meta::Method::Parameter paramTemplate
                        = {{nullptr},
                           istring(g_param_spec_get_name(paramSpecs[i])),
                           plugin.fromGType(paramSpecs[i]->value_type),
                           {defaultValue}};
                    new(&parameters[j]) Meta::Method::Parameter(paramTemplate);
                    j++;
                }
            }
        }

        Meta::Method::Overload overloadTemplate
            = {{nullptr},
               {parameters, constructorParameterCount},
               Meta::Type::makeType(metaclass, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable),
               false,
               &Constructor::call};
        new(overload) Meta::Method::Overload(overloadTemplate);

        Constructor ctorTemplate = {{{nullptr}, istring(""), {overload, 1}}, type};
        new(constructor) Constructor(ctorTemplate);
        cls->constructor.set(&constructor->metaMethod);
    }
    g_type_class_unref(objectClass);
    motor_forceuse(propertyCount);
}  // namespace Gtk3

bool registerGObjectClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert_format(G_TYPE_FUNDAMENTAL(type) == G_TYPE_OBJECT,
                        "expected GObject type, got {0} which is a {1}", g_type_name(type),
                        g_type_name(G_TYPE_FUNDAMENTAL(type)));
    auto* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGObjectClass(plugin, parent) : motor_class< GObjectWrapper >();
        Meta::Class clsTemplate = {istring(g_type_name(type)),
                                   parentClass->size,
                                   parentClass,
                                   0,
                                   parentClass->objects,
                                   parentClass->tags,
                                   parentClass->properties,
                                   parentClass->methods,
                                   {nullptr},
                                   parentClass->operators,
                                   parentClass->copyconstructor,
                                   parentClass->destructor};

        new(cls) Meta::Class(clsTemplate);
        completeGObjectClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        plugin.registerValue(cls->name, Meta::Value(registry));
        return true;
    }
    else
        return false;
}

raw< const Meta::Class > getGObjectClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert_format(G_TYPE_FUNDAMENTAL(type) == G_TYPE_OBJECT,
                        "expected GObject type, got {0} which is a {1}", g_type_name(type),
                        g_type_name(G_TYPE_FUNDAMENTAL(type)));
    auto* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGObjectClass(plugin, parent) : motor_class< GObjectWrapper >();
        Meta::Class clsTemplate = {istring(g_type_name(type)),
                                   parentClass->size,
                                   parentClass,
                                   0,
                                   parentClass->objects,
                                   parentClass->tags,
                                   parentClass->properties,
                                   parentClass->methods,
                                   {nullptr},
                                   parentClass->operators,
                                   parentClass->copyconstructor,
                                   parentClass->destructor};

        new(cls) Meta::Class(clsTemplate);
        completeGObjectClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        plugin.registerValue(cls->name, Meta::Value(registry));
    }
    return raw< const Meta::Class > {cls};
}

void destroyGObjectClass(Gtk3Plugin& plugin, GType type)
{
    auto* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(cls && cls->constructor)
    {
        for(const auto& overload: cls->constructor->overloads)
        {
            for(const auto& param: overload.parameters)
            {
                if(param.defaultValue) param.defaultValue->~Value();
            }
        }
    }
    else if(!cls)
    {
        motor_info_format(Log::gtk(), "Type not registered: {0}", g_type_name(type));
    }
}

}}  // namespace Motor::Gtk3
