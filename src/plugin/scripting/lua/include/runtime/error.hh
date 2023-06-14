/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_LUA_RUNTIME_ERROR_HH
#define MOTOR_PLUGIN_SCRIPTING_LUA_RUNTIME_ERROR_HH

#include <stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Lua {

int error(lua_State* state, const char* message);

}}  // namespace Motor::Lua

#endif
