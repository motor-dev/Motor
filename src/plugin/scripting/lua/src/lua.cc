/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <lua.meta.hh>

namespace Motor {

LuaScript::LuaScript(const weak< const File >& file) : Script< LuaScript >(file)
{
}

LuaScript::~LuaScript() = default;

}  // namespace Motor
