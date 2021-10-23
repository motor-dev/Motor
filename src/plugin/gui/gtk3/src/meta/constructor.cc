/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <meta/constructor.meta.hh>

#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

Meta::Value Constructor::call(raw< const Meta::Method > method, Meta::Value* params, u32 nparams)
{
    motor_forceuse(method);
    motor_forceuse(params);
    motor_forceuse(nparams);
    return Meta::Value();
}

}}  // namespace Motor::Gtk3
