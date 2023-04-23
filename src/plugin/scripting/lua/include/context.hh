/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/value.hh>
#include <motor/plugin/plugin.hh>
#include <motor/scriptengine.hh>
#include <lua.meta.hh>

namespace Motor { namespace Lua {

class Context : public ScriptEngine< LuaScript >
{
private:
    lua_State* m_state;

public:
    explicit Context(const Plugin::Context& context);
    ~Context() override;

    static minitl::format_buffer< 1024u > tostring(lua_State* state, int element);
    static void                           printStack(lua_State* l);
    static void typeError(lua_State* state, int narg, const char* expected, const char* got);
    static void typeError(lua_State* state, int narg, const Meta::Type& expected, const char* got);
    static int  push(lua_State* state, const Meta::Value& v);
    static void checkArg(lua_State* state, int narg, int type);
    static void checkArg(lua_State* state, int narg, const char* userDataType);
    static void checkArg(lua_State* state, int narg, const Meta::Type& type);
    static minitl::format_buffer< 1024u > getCallInfo(lua_State* state);

private:
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         handle) override;
    void runBuffer(const weak< const LuaScript >& script, Resource::Resource& resource,
                   const minitl::Allocator::Block< u8 >& buffer) override;
    void reloadBuffer(const weak< const LuaScript >& script, Resource::Resource& resource,
                      const minitl::Allocator::Block< u8 >& buffer) override;

    static void* luaAlloc(void* ud, void* ptr, size_t osize, size_t nsize);
};

}}  // namespace Motor::Lua
