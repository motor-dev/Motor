/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

bool convertMetaValueToGValue(const Meta::Value& value, GType type, GValue* target);

}}  // namespace Motor::Gtk3
