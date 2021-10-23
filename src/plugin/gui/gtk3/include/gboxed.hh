/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GBOXED_HH_
#define MOTOR_UI_GTK3_GBOXED_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGBoxedClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
