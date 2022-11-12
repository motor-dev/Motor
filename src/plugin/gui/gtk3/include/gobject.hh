/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGObjectClass(Gtk3Plugin& plugin, GType type);
void                     destroyGObjectClass(Gtk3Plugin& plugin, GType type);

void storeMetaValue(const Meta::Value& value, GValue* target);

}}  // namespace Motor::Gtk3
