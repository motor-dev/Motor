/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_LUA_STDAFX_H_
#define MOTOR_LUA_STDAFX_H_
/**************************************************************************************************/

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

/**************************************************************************************************/
#endif
