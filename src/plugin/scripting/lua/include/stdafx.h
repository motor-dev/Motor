/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_LUA_STDAFX_H
#define MOTOR_PLUGIN_SCRIPTING_LUA_STDAFX_H

#include <motor/stdafx.h>

#define MOTOR_API_LUA

extern "C"
{
#include <lauxlib.h>
#include <lua.h>
#include <lualib.h>
}

namespace Motor { namespace Log {
weak< Logger > lua();
}} // namespace Motor::Log

#endif
