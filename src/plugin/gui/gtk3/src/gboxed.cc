/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gboxed.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGBoxedClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_forceuse(plugin);
    motor_forceuse(cls);
    motor_forceuse(type);
}

raw< const Meta::Class > getGBoxedClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert_format(G_TYPE_FUNDAMENTAL(type) == G_TYPE_BOXED,
                        "expected GBoxed type, got {0} which is a {1}", g_type_name(type),
                        g_type_name(G_TYPE_FUNDAMENTAL(type)));
    auto* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);

        cls = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGBoxedClass(plugin, parent) : motor_class< GBoxedWrapper >();
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
        completeGBoxedClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        cls->owner = plugin.registerValue(istring(g_type_name(type)), Meta::Value(registry));
    }
    raw< const Meta::Class > result = {cls};
    return result;
}

}}  // namespace Motor::Gtk3
