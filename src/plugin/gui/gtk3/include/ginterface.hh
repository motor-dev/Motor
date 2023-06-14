/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GINTERFACE_HH
#define MOTOR_PLUGIN_GUI_GTK3_GINTERFACE_HH

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGInterfaceClass(Gtk3Plugin& plugin, GType type);
void                     destroyGInterfaceClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

#endif
