/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GINTERFACE_HH_
#define MOTOR_UI_GTK3_GINTERFACE_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGInterfaceClass(Gtk3Plugin& plugin, GType type);
void                     destroyGInterfaceClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
