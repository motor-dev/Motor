/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

extern "C"
{
#include <lauxlib.h>
#include <lua.h>
#include <lualib.h>
}

namespace Motor { namespace Log {

weak< Logger > lua();

}}  // namespace Motor::Log
