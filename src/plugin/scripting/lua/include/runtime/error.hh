/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Lua {

int error(lua_State* state, const minitl::format< 4096u >& message);

}}  // namespace Motor::Lua
