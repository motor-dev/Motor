/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GENUM_HH
#define MOTOR_PLUGIN_GUI_GTK3_GENUM_HH

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGEnumClass(Gtk3Plugin& plugin, GType type);
}}  // namespace Motor::Gtk3

#endif
