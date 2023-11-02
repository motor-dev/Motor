/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <lua.meta.hh>

namespace Motor {

LuaScript::LuaScript(const weak< const File >& script) : Script< LuaScript >(script)
{
}

LuaScript::~LuaScript() = default;

}  // namespace Motor
