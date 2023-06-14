/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GBOXED_HH
#define MOTOR_PLUGIN_GUI_GTK3_GBOXED_HH

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGBoxedClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

#endif
