/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#ifndef MOTOR_LUA_RUNTIME_VALUE_HH_
#define MOTOR_LUA_RUNTIME_VALUE_HH_
/**************************************************************************************************/
#include <stdafx.h>

namespace Motor { namespace Lua {

bool createValue(lua_State* state, int index, const Meta::Type& type, void* buffer);

}}  // namespace Motor::Lua

/**************************************************************************************************/
#endif
