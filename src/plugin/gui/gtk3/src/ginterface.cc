/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <ginterface.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>
#include <meta/property.meta.hh>

#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGInterfaceClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_forceuse(plugin);
    motor_forceuse(cls);
    motor_info_format(Log::gtk(), "finishing registration of interface {0}", g_type_name(type));
    if(type != G_TYPE_INTERFACE)
    {
        auto*        interface = static_cast< GTypeInterface* >(g_type_default_interface_ref(type));
        guint        paramSpecCount;
        GParamSpec** paramSpecs    = g_object_interface_list_properties(interface, &paramSpecCount);
        u32          propertyCount = 0;
        u32          constructorParameterCount = 0;
        for(guint i = 0; i < paramSpecCount; ++i)
        {
            if(paramSpecs[i]->flags & (G_PARAM_WRITABLE | G_PARAM_CONSTRUCT)
               && !(paramSpecs[i]->flags & G_PARAM_DEPRECATED))
            {
                constructorParameterCount++;
            }
            if(paramSpecs[i]->flags & (G_PARAM_READABLE | G_PARAM_WRITABLE)
               && !(paramSpecs[i]->flags & (G_PARAM_CONSTRUCT_ONLY | G_PARAM_DEPRECATED)))
            {
                propertyCount++;
            }
        }
        motor_forceuse(propertyCount);
        motor_forceuse(constructorParameterCount);
        g_type_default_interface_unref(interface);
    }
}  // namespace Gtk3

raw< const Meta::Class > getGInterfaceClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert_format(G_TYPE_FUNDAMENTAL(type) == G_TYPE_INTERFACE,
                        "expected GInterface type, got {0} which is a {1}", g_type_name(type),
                        g_type_name(G_TYPE_FUNDAMENTAL(type)));
    auto* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGInterfaceClass(plugin, parent) : motor_class< GObjectWrapper >();
        Meta::Class clsTemplate = {parentClass->size,
                                   parentClass,
                                   0,
                                   {nullptr},
                                   parentClass->objects,
                                   parentClass->tags,
                                   parentClass->properties,
                                   parentClass->methods,
                                   {nullptr},
                                   parentClass->interfaces,
                                   parentClass->copyconstructor,
                                   parentClass->destructor};

        new(cls) Meta::Class(clsTemplate);
        completeGInterfaceClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        cls->owner = plugin.registerValue(istring(g_type_name(type)), Meta::Value(registry));
    }
    raw< const Meta::Class > result = {cls};
    return result;
}

void destroyGInterfaceClass(Gtk3Plugin& plugin, GType type)
{
    motor_info_format(Log::gtk(), "destroying interface {0}", g_type_name(type));
    motor_forceuse(plugin);
    motor_forceuse(type);
}

}}  // namespace Motor::Gtk3
