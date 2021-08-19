/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <lua.script.hh>

namespace Motor {

LuaScript::LuaScript(weak< const File > file) : Script(file)
{
}

LuaScript::~LuaScript()
{
}

}  // namespace Motor
