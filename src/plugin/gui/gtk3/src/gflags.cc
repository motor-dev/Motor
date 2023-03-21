/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gflags.hh>
#include <gtk3plugin.hh>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

static void completeGFlagsClass(Gtk3Plugin& plugin, Meta::Class* cls, GType type)
{
    motor_forceuse(plugin);
    motor_forceuse(cls);
    motor_forceuse(type);
}

raw< const Meta::Class > getGFlagsClass(Gtk3Plugin& plugin, GType type)
{
    motor_assert_format(G_TYPE_FUNDAMENTAL(type) == G_TYPE_FLAGS,
                        "expected GFlags type, got {0} which is a {1}", g_type_name(type),
                        g_type_name(G_TYPE_FUNDAMENTAL(type)));
    Meta::Class* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, plugin.quark()));
    if(!cls)
    {
        GType parent = g_type_parent(type);
        cls          = plugin.allocate< Meta::Class >();
        g_type_set_qdata(type, plugin.quark(), cls);
        raw< const Meta::Class > parentClass
            = parent ? getGFlagsClass(plugin, parent) : motor_class< GFlagsWrapper >();
        Meta::Class clsTemplate = {istring(g_type_name(type)),
                                   parentClass->size,
                                   0,
                                   Meta::ClassType_Number,
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
        completeGFlagsClass(plugin, cls, type);
        raw< const Meta::Class > registry = {cls};
        plugin.registerValue(cls->name, Meta::Value(registry));
    }
    raw< const Meta::Class > result = {cls};
    return result;
}

}}  // namespace Motor::Gtk3
