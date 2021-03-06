/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <ginterface.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>
#include <meta/property.meta.hh>

#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGInterfaceClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_forceuse(plugin);
    motor_forceuse(cls);
    motor_debug("finishing registration of interface %s" | g_type_name(type));
    if(type != G_TYPE_INTERFACE)
    {
        GTypeInterface* interface = static_cast< GTypeInterface* >(
            g_type_default_interface_ref(type));
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
        g_type_default_interface_unref(interface);
    }
}  // namespace Gtk3

raw< const Meta::Class > getGInterfaceClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert(G_TYPE_FUNDAMENTAL(type) == G_TYPE_INTERFACE,
                 "expected GInterface type, got %s which is a %s" | g_type_name(type)
                     | g_type_name(G_TYPE_FUNDAMENTAL(type)));
    Meta::Class* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGInterfaceClass(plugin, parent) : motor_class< GObjectWrapper >();
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
        completeGInterfaceClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        plugin.registerValue(cls->name, Meta::Value(registry));
    }
    raw< const Meta::Class > result = {cls};
    return result;
}

void destroyGInterfaceClass(Gtk3Plugin& plugin, GType type)
{
    motor_forceuse(plugin);
    motor_forceuse(type);
}

}}  // namespace Motor::Gtk3
