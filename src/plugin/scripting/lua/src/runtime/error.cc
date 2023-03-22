/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>
#include <context.hh>
#include <runtime/error.hh>

namespace Motor { namespace Lua {

int error(lua_State* state, const char* message)
{
    return luaL_error(state, "%s: %s", Context::getCallInfo(state).c_str(), message);
}

}}  // namespace Motor::Lua
