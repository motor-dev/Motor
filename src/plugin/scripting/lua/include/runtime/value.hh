/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_LUA_RUNTIME_VALUE_HH
#define MOTOR_PLUGIN_SCRIPTING_LUA_RUNTIME_VALUE_HH

#include <stdafx.h>

namespace Motor { namespace Lua {

bool createValue(lua_State* state, int index, const Meta::Type& type, void* buffer);

}}  // namespace Motor::Lua

#endif
