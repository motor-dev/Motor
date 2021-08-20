/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#ifndef MOTOR_LUA_RUNTIME_CALL_HH_
#define MOTOR_LUA_RUNTIME_CALL_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Lua {

int call(lua_State* state, raw< const Meta::Method > method);

}}  // namespace Motor::Lua

/**************************************************************************************************/
#endif
