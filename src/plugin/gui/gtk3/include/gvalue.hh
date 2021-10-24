/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GVALUE_HH_
#define MOTOR_UI_GTK3_GVALUE_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Gtk3 {

bool convertMetaValueToGValue(const Meta::Value& value, GType type, GValue* target);

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
