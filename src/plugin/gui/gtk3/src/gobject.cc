/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gobject.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>
#include <meta/constructor.meta.hh>
#include <meta/property.meta.hh>

#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGObjectClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_debug("finishing registration of type %s" | g_type_name(type));
    GObjectClass* objectClass = static_cast< GObjectClass* >(g_type_class_ref(type));
    guint         paramSpecCount;
    GParamSpec**  paramSpecs    = g_object_class_list_properties(objectClass, &paramSpecCount);
    u32           propertyCount = 0;
    u32           constructorParameterCount = 0;
    for(guint i = 0; i < paramSpecCount; ++i)
    {
        if(paramSpecs[i]->value_type == G_TYPE_POINTER
           || paramSpecs[i]->value_type == G_TYPE_VARIANT)
        {
            motor_warning("skipping property %s.%s of type %s" | g_type_name(type)
                          | g_param_spec_get_name(paramSpecs[i])
                          | g_type_name(paramSpecs[i]->value_type));
            continue;
        }
        if(paramSpecs[i]->flags & G_PARAM_DEPRECATED)
        {
            motor_spam("skipping deprecated property %s.%s" | g_type_name(type)
                       | g_param_spec_get_name(paramSpecs[i]));
            continue;
        }
        if(paramSpecs[i]->flags & (G_PARAM_READWRITE | G_PARAM_CONSTRUCT))
        {
            constructorParameterCount++;
        }
        if((paramSpecs[i]->flags & G_PARAM_READABLE)
           && !(paramSpecs[i]->flags & G_PARAM_CONSTRUCT_ONLY))
        {
            propertyCount++;
        }
        if((paramSpecs[i]->flags & G_PARAM_WRITABLE) && !(paramSpecs[i]->flags & G_PARAM_READABLE))
        {
            motor_warning("skipping signal property %s.%s [%s]\n    %s" | g_type_name(type)
                          | g_param_spec_get_name(paramSpecs[i])
                          | g_type_name(paramSpecs[i]->value_type)
                          | g_param_spec_get_blurb(paramSpecs[i]));
        }
    }
    if(G_TYPE_IS_INSTANTIATABLE(type))
    {
        Constructor*             constructor = plugin.allocate< Constructor >();
        Meta::Method::Overload*  overload    = plugin.allocate< Meta::Method::Overload >();
        Meta::Method::Parameter* parameters  = 0;
        raw< const Meta::Class > metaclass   = {cls};
        if(constructorParameterCount)
        {
            parameters = plugin.allocateArray< Meta::Method::Parameter >(constructorParameterCount);
            for(guint i = 0, j = 0; i < paramSpecCount; ++i)
            {
                // motor_assert(istring("child") != istring(g_param_spec_get_name(paramSpecs[i])),
                //             "hop");
                if(paramSpecs[i]->value_type == G_TYPE_POINTER
                   || paramSpecs[i]->value_type == G_TYPE_VARIANT
                   || (paramSpecs[i]->flags & G_PARAM_DEPRECATED))
                {
                    continue;
                }
                if(paramSpecs[i]->flags & (G_PARAM_READWRITE | G_PARAM_CONSTRUCT))
                {
                    Meta::Value* defaultValue = plugin.allocate< Meta::Value >();
                    new(defaultValue) Meta::Value(
                        plugin.fromGValue(g_param_spec_get_default_value(paramSpecs[i])));
                    Meta::Method::Parameter paramTemplate
                        = {{0},
                           istring(g_param_spec_get_name(paramSpecs[i])),
                           plugin.fromGType(paramSpecs[i]->value_type),
                           {defaultValue}};
                    new(&parameters[j]) Meta::Method::Parameter(paramTemplate);
                    j++;
                }
            }
        }

        Meta::Method::Overload overloadTemplate
            = {{0},
               {constructorParameterCount, parameters},
               Meta::Type::makeType(metaclass, Meta::Type::RefPtr, Meta::Type::Mutable,
                                    Meta::Type::Mutable),
               false,
               &Constructor::call};
        new(overload) Meta::Method::Overload(overloadTemplate);

        Constructor ctorTemplate
            = {{Meta::Class::nameConstructor(), {1, overload}, {&constructor->metaMethod}}, type};
        new(constructor) Constructor(ctorTemplate);
        cls->constructor.set(&constructor->metaMethod);
    }
    g_type_class_unref(objectClass);
}  // namespace Gtk3

raw< const Meta::Class > getGObjectClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert(G_TYPE_FUNDAMENTAL(type) == G_TYPE_OBJECT,
                 "expected GObject type, got %s which is a %s" | g_type_name(type)
                     | g_type_name(G_TYPE_FUNDAMENTAL(type)));
    Meta::Class* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGObjectClass(plugin, parent) : motor_class< GObjectWrapper >();
        Meta::Class clsTemplate = {istring(g_type_name(type)),
                                   parentClass->size,
                                   0,
                                   Meta::ClassType_Struct,
                                   {0},
                                   parentClass,
                                   {0},
                                   {0},
                                   {0, 0},
                                   {0, 0},
                                   {0},
                                   Meta::OperatorTable::s_emptyTable,
                                   parentClass->copyconstructor,
                                   parentClass->destructor};

        new(cls) Meta::Class(clsTemplate);
        completeGObjectClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        plugin.registerValue(cls->name, Meta::Value(registry));
    }
    raw< const Meta::Class > result = {cls};
    return result;
}

void destroyGObjectClass(Gtk3Plugin& plugin, GType type)
{
    motor_forceuse(plugin);
    Meta::Class* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(cls->constructor)
    {
        for(u32 i = 0; i < cls->constructor->overloads.count; ++i)
        {
            const Meta::Method::Overload& overload = cls->constructor->overloads[i];
            for(u32 j = 0; j < overload.params.count; ++j)
            {
                const Meta::Method::Parameter& param = overload.params[j];
                if(param.defaultValue) param.defaultValue->~Value();
            }
        }
    }
}

}}  // namespace Motor::Gtk3
