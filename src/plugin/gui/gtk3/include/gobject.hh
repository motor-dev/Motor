/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GOBJECT_HH_
#define MOTOR_UI_GTK3_GOBJECT_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGObjectClass(Gtk3Plugin& plugin, GType type);
void                     destroyGObjectClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
