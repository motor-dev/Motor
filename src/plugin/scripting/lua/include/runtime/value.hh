/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */
#pragma once

#include <stdafx.h>

namespace Motor { namespace Lua {

bool createValue(lua_State* state, int index, const Meta::Type& type, void* buffer);

}}  // namespace Motor::Lua
