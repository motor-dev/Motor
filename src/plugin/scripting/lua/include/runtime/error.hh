/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#ifndef MOTOR_LUA_RUNTIME_ERROR_HH_
#define MOTOR_LUA_RUNTIME_ERROR_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/meta/engine/methodinfo.script.hh>

namespace Motor { namespace Lua {

int error(lua_State* state, const minitl::format< 4096u >& message);

}}  // namespace Motor::Lua

/**************************************************************************************************/
#endif
