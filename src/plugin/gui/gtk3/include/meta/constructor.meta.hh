/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_META_CONSTRUCTOR_META_HH
#define MOTOR_PLUGIN_GUI_GTK3_META_CONSTRUCTOR_META_HH

#include <stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Gtk3 {

struct Constructor
{
    Meta::Method metaMethod;

public:
    const GType type {};

    static Meta::Value call(raw< const Meta::Method > method, Meta::Value* params, u32 nparams);
};

}}  // namespace Motor::Gtk3

#endif
