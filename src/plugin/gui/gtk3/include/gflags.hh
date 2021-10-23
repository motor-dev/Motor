/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GFLAGS_HH_
#define MOTOR_UI_GTK3_GFLAGS_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGFlagsClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
