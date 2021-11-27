/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_LUA_LUA_META_HH_
#define MOTOR_LUA_LUA_META_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.meta.hh>

namespace Motor {

class LuaScript : public Script
{
    friend class PackageLoader;
    published : LuaScript(motor_tag(EditHint::Extension(".lua")) weak< const File > script);
    ~LuaScript();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
