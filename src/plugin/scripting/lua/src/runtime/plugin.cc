/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>

#include <motor/plugin/plugin.hh>
#include <context.hh>
#include <runtime/plugin.hh>

namespace Motor { namespace Lua {

static int pluginGC(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Plugin");
    auto* userdata = (Plugin::Plugin< void >*)lua_touserdata(state, 1);
    userdata->~Plugin();
    return 0;
}

static int pluginToString(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Plugin");
    auto* userdata = (Plugin::Plugin< void >*)lua_touserdata(state, 1);
    lua_pushfstring(state, "plugin[%s]", userdata->name().str().name);
    return 1;
}

static int pluginGet(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Plugin");
    Context::checkArg(state, 2, LUA_TSTRING);

    auto*       userdata = (Plugin::Plugin< void >*)lua_touserdata(state, 1);
    const char* name     = lua_tostring(state, 2);
    Meta::Value v(userdata->pluginNamespace());
    Context::push(state, v[istring(name)]);
    return 1;
}

const luaL_Reg s_pluginMetaTable[] = {{"__gc", pluginGC},
                                      {"__tostring", pluginToString},
                                      {"__index", pluginGet},
                                      {nullptr, nullptr}};

}}  // namespace Motor::Lua
