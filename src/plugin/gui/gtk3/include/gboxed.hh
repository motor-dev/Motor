/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

raw< const Meta::Class > getGBoxedClass(Gtk3Plugin& plugin, GType type);

}}  // namespace Motor::Gtk3
