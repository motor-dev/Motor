/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GOBJECT_HH
#define MOTOR_PLUGIN_GUI_GTK3_GOBJECT_HH

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

bool                     registerGObjectClass(Gtk3Plugin& plugin, GType type);
raw< const Meta::Class > getGObjectClass(Gtk3Plugin& plugin, GType type);
void                     destroyGObjectClass(Gtk3Plugin& plugin, GType type);

void storeMetaValue(const Meta::Value& value, GValue* target);

}}  // namespace Motor::Gtk3

#endif
