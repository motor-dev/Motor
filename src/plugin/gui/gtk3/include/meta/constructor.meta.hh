/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Gtk3 {

struct Constructor
{
    Meta::Method metaMethod;

public:
    const GType type;

    static Meta::Value call(raw< const Meta::Method > method, Meta::Value* params, u32 nparams);
};

}}  // namespace Motor::Gtk3
