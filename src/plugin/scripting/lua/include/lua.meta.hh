/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_LUA_LUA_META_HH
#define MOTOR_PLUGIN_SCRIPTING_LUA_LUA_META_HH

#include <stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class LuaScript : public Script< LuaScript >
{
    friend class PackageLoader;

public:
    explicit LuaScript(
        [[motor::meta(EditHint::Extension(".lua"))]] const weak< const File >& script);
    ~LuaScript() override;
};

}  // namespace Motor

#include <lua.meta.factory.hh>
#endif
