/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>

#include <motor/resource/resourcemanager.hh>
#include <context.hh>
#include <runtime/resource.hh>

namespace Motor { namespace Lua {

struct ResourceToken
{
    weak< Resource::ResourceManager >    manager;
    raw< const Meta::Class >             type {};
    weak< const Resource::IDescription > description;
};

static int resourceLoaderGC(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.ResourceManager");
    auto* userdata = (weak< Resource::ResourceManager >*)lua_touserdata(state, 1);
    userdata->~weak();
    return 0;
}

static int resourceLoaderToString(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.ResourceManager");
    auto* userdata = (weak< Resource::ResourceManager >*)lua_touserdata(state, 1);
    lua_pushfstring(state, "resourcemanager[%p]", userdata->operator->());
    return 1;
}

static int resourceLoaderLoad(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.ResourceManager");
    Context::checkArg(state, 2, "Motor.Object");

    weak< Resource::ResourceManager > userdata
        = *(weak< Resource::ResourceManager >*)lua_touserdata(state, 1);
    auto* v             = (Meta::Value*)lua_touserdata(state, 2);
    auto  description   = v->as< weak< const Resource::IDescription > >();
    auto* resourceToken = (ResourceToken*)lua_newuserdata(state, sizeof(ResourceToken));
    new((void*)resourceToken) ResourceToken;
    resourceToken->description = description;
    resourceToken->manager     = userdata;
    resourceToken->type        = v->type().metaclass;
    userdata->load(resourceToken->type, description);
    luaL_getmetatable(state, "Motor.Resource");
    lua_setmetatable(state, -2);
    return 1;
}

const luaL_Reg s_resourceLoaderMetaTable[] = {{"__gc", resourceLoaderGC},
                                              {"__tostring", resourceLoaderToString},
                                              {"load", resourceLoaderLoad},
                                              {nullptr, nullptr}};

static int resourceGC(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Resource");
    auto* userdata = (ResourceToken*)lua_touserdata(state, 1);
    userdata->manager->unload(userdata->type, userdata->description);
    userdata->~ResourceToken();
    return 0;
}

static int resourceToString(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Resource");
    auto* userdata = (ResourceToken*)lua_touserdata(state, 1);
    lua_pushfstring(state, "Resource<%s>[%p]", userdata->type->fullname().str().name,
                    userdata->description.operator->());
    return 1;
}

const luaL_Reg s_resourceMetaTable[]
    = {{"__gc", resourceGC}, {"__tostring", resourceToString}, {nullptr, nullptr}};

}}  // namespace Motor::Lua
