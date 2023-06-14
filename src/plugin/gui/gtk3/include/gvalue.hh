/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GVALUE_HH
#define MOTOR_PLUGIN_GUI_GTK3_GVALUE_HH

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

bool convertMetaValueToGValue(const Meta::Value& value, GType type, GValue* target);

}}  // namespace Motor::Gtk3

#endif
