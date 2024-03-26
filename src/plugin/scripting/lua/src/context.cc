/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <motor/meta/interfacetable.hh>
#include <context.hh>
#include <runtime/object.hh>
#include <runtime/plugin.hh>
#include <runtime/resource.hh>

namespace Motor {

namespace Arena {
static minitl::allocator& lua()
{
    return script();
}
}  // namespace Arena

namespace Lua {

static const raw< const Meta::Class > s_voidClass = motor_class< void >();

static const char* s_metaTables[]
    = {"Motor.Object", "Motor.Resource", "Motor.ResourceManager", "Motor.Plugin"};

static const luaL_Reg loadedlibs[] = {{"_G", luaopen_base},
                                      //{LUA_LOADLIBNAME, luaopen_package},
                                      {LUA_COLIBNAME, luaopen_coroutine},
                                      {LUA_TABLIBNAME, luaopen_table},
#if 0
                                      {LUA_IOLIBNAME, luaopen_io},
                                      {LUA_OSLIBNAME, luaopen_os},
#endif
                                      {LUA_STRLIBNAME, luaopen_string},
#if 0
                                      {LUA_BITLIBNAME, luaopen_bit32},
#endif
                                      {LUA_MATHLIBNAME, luaopen_math},
                                      {LUA_DBLIBNAME, luaopen_debug},
                                      {nullptr, nullptr}};

void Context::typeError(lua_State* state, int narg, const char* expected, const char* got)
{
    Context::printStack(state);
    const char* msg = lua_pushfstring(state, "%s expected, got %s", expected, got);
    luaL_argerror(state, narg, msg);
}

void Context::typeError(lua_State* state, int narg, const Meta::Type& expected, const char* got)
{
    Context::printStack(state);
    const char* msg = lua_pushfstring(state, "%s expected, got %s",
                                      minitl::format< 1024 >(FMT("{0}"), expected), got);
    luaL_argerror(state, narg, msg);
}

void Context::checkArg(lua_State* state, int narg, int type)
{
    if(lua_type(state, narg) != type)
    {
        typeError(state, narg, lua_typename(state, type), luaL_typename(state, narg));
    }
}

void Context::checkArg(lua_State* state, int narg, const char* userDataType)
{
    if(lua_type(state, narg) != LUA_TUSERDATA)
    {
        typeError(state, narg, userDataType, luaL_typename(state, narg));
    }
    lua_getmetatable(state, narg);
    luaL_getmetatable(state, userDataType);
    if(!lua_rawequal(state, -1, -2))
    {
        lua_pop(state, 1);
        const char* typeName = luaL_typename(state, narg);
        for(const char* metatable: s_metaTables)
        {
            luaL_getmetatable(state, metatable);
            if(lua_rawequal(state, -1, -2))
            {
                typeName = metatable;
            }
            lua_pop(state, 1);
        }
        lua_pop(state, 1);
        typeError(state, narg, userDataType, typeName);
    }
    lua_pop(state, 2);
}

void Context::checkArg(lua_State* state, int narg, const Meta::Type& type)
{
    if(lua_type(state, narg) != LUA_TUSERDATA)
    {
        typeError(state, narg, type, luaL_typename(state, narg));
    }
    lua_getmetatable(state, narg);
    luaL_getmetatable(state, "Motor.Object");
    if(!lua_rawequal(state, -1, -2))
    {
        lua_pop(state, 1);
        const char* typeName = luaL_typename(state, narg);
        for(const char* metatable: s_metaTables)
        {
            luaL_getmetatable(state, metatable);
            if(lua_rawequal(state, -1, -2))
            {
                typeName = metatable;
            }
            lua_pop(state, 1);
        }
        lua_pop(state, 1);
        typeError(state, narg, type, typeName);
    }
    lua_pop(state, 2);
    auto* value = (Meta::Value*)lua_touserdata(state, narg);
    if(!value->type().isA(type))
    {
        typeError(state, narg, type, minitl::format<>(FMT("{0}"), value->type()));
    }
}

int Context::push(lua_State* state, const Meta::Value& v)
{
    const Meta::Type& t = v.type();
    if(t.metaclass == s_voidClass)
    {
        return 0;
    }
    else if(v.type().indirection >= Meta::Type::Indirection::RawPtr
            && v.as< const void* const >() == nullptr)
    {
        lua_pushnil(state);
        return 1;
    }
    else if(t.metaclass->interfaces->i64Interface)
    {
        lua_pushinteger(state, (lua_Integer)(*t.metaclass->interfaces->i64Interface->get)(v));
        return 1;
    }
    else if(t.metaclass->interfaces->u64Interface)
    {
        lua_pushinteger(state, (lua_Integer)(*t.metaclass->interfaces->u64Interface->get)(v));
        return 1;
    }
    else if(t.metaclass->interfaces->boolInterface)
    {
        lua_pushboolean(state, (*t.metaclass->interfaces->boolInterface->get)(v));
        return 1;
    }
    else if(t.metaclass->interfaces->charpInterface)
    {
        lua_pushstring(state, (*t.metaclass->interfaces->charpInterface->get)(v));
        return 1;
    }
    else if(t.metaclass->interfaces->doubleInterface)
    {
        lua_pushnumber(state, (lua_Number)(*t.metaclass->interfaces->doubleInterface->get)(v));
        return 1;
    }
    else if(t.metaclass->interfaces->floatInterface)
    {
        lua_pushnumber(state, (lua_Number)(*t.metaclass->interfaces->floatInterface->get)(v));
        return 1;
    }
    else
    {
        void* userdata = lua_newuserdata(state, sizeof(Meta::Value));
        new(userdata) Meta::Value(v);
        luaL_getmetatable(state, "Motor.Object");
        lua_setmetatable(state, -2);
        return 1;
    }
}

minitl::format_buffer< 1024u > Context::tostring(lua_State* state, int element)
{
    int t = lua_type(state, element);
    switch(t)
    {
    case LUA_TSTRING:
        return minitl::format< 1024u >(FMT("lua_string('{0}')"), lua_tostring(state, element));
    case LUA_TBOOLEAN:
        return minitl::format< 1024u >(FMT("lua_boolean({0})"), lua_toboolean(state, element));
    case LUA_TNUMBER:
        return minitl::format< 1024u >(FMT("lua_number({0})"), lua_tonumber(state, element));
    case LUA_TUSERDATA:
    {
        lua_getmetatable(state, element);
        luaL_getmetatable(state, "Motor.Object");
        if(lua_rawequal(state, -1, -2))
        {
            lua_pop(state, 2);
            auto* userdata = (Meta::Value*)lua_touserdata(state, element);
            return minitl::format<>(FMT("({0}[{1}]"),
                                    userdata->type().metaclass->fullname().str().c_str(), userdata);
        }
        lua_pop(state, 1);
        luaL_getmetatable(state, "Motor.Plugin");
        if(lua_rawequal(state, -1, -2))
        {
            lua_pop(state, 2);
            auto* userdata = (Plugin::Plugin< void >*)lua_touserdata(state, element);
            return minitl::format< 1024u >(FMT("Motor.Plugin[{0}]"), userdata->name());
        }
        lua_pop(state, 1);
        luaL_getmetatable(state, "Motor.ResourceManager");
        if(lua_rawequal(state, -1, -2))
        {
            lua_pop(state, 2);
            return minitl::format_buffer< 1024u > {"Motor.ResourceManager"};
        }
        lua_pop(state, 1);
        luaL_getmetatable(state, "Motor.Resource");
        if(lua_rawequal(state, -1, -2))
        {
            lua_pop(state, 2);
            return minitl::format_buffer< 1024u > {"Motor.Resource"};
        }
        else
        {
            lua_pop(state, 2);
            return minitl::format< 1024u >(FMT("lua_userdata[{0}]"),
                                           lua_touserdata(state, element));
        }
    }
    default: return minitl::format< 1024u >(FMT("{0}"), lua_typename(state, t));
    }
}

void Context::printStack(lua_State* state)
{
    int i;
    int top = lua_gettop(state);

    motor_debug_format(Log::lua(), "total in stack {0}\n", top);

    for(i = 1; i <= top; i++)
    {
        motor_debug_format(Log::lua(), " {0}: {1}", (top - i + 1), tostring(state, -i).c_str());
    }
}

extern "C" int luaPrint(lua_State* L)
{
    int n = lua_gettop(L); /* number of arguments */
    int i;
    lua_getglobal(L, "tostring");
    for(i = 1; i <= n; i++)
    {
        const char* s;
        lua_pushvalue(L, -1); /* function to be called */
        lua_pushvalue(L, i);  /* value to print */
        lua_call(L, 1, 1);
        s = lua_tostring(L, -1); /* get result */
        if(s == nullptr) return luaL_error(L, "'tostring' must return a string to 'print'");
        lua_Debug ar;
        if(lua_getstack(L, 1, &ar))
        {
            lua_getinfo(L, "Snl", &ar);
            Log::lua()->log(logInfo, ar.source, ar.currentline, s);
        }
        else
        {
            Log::lua()->log(logInfo, MOTOR_FILE, MOTOR_LINE, s);
        }
        lua_pop(L, 1); /* pop result */
    }
    return 0;
}

extern "C" int luaPlugin(lua_State* state)
{
    int n = lua_gettop(state); /* number of arguments */
    if(n != 1)
    {
        return luaL_error(state, "plugin method expects one argument; got %d", n);
    }
    const char* pluginName = lua_tostring(state, -1);
    void*       userdata   = lua_newuserdata(state, sizeof(Plugin::Plugin< void >));
    new(userdata) Plugin::Plugin< void >(inamespace(pluginName), Plugin::Plugin< void >::Preload);
    luaL_getmetatable(state, "Motor.Plugin");
    lua_setmetatable(state, -2);
    return 1;
}

extern "C" int luaGet(lua_State* state)
{
    int n = lua_gettop(state); /* number of arguments */
    if(n != 2)
    {
        return luaL_error(state, "getattr method expects two arguments; got %d", n);
    }
    Context::checkArg(state, 1, "Motor.Object");
    Context::checkArg(state, 2, LUA_TSTRING);

    auto*       userdata = (Meta::Value*)lua_touserdata(state, -2);
    const char* name     = lua_tostring(state, -1);
    Meta::Value v        = (*userdata)[istring(name)];
    if(!v)
    {
        lua_pushnil(state);
        return 1;
    }
    Context::push(state, v);
    return 1;
}

extern "C" int luaGetType(lua_State* state)
{
    int n = lua_gettop(state); /* number of arguments */
    if(n != 1)
    {
        return luaL_error(state, "getattr method expects one argument; got %d", n);
    }
    Context::checkArg(state, 1, "Motor.Object");

    auto* userdata = (Meta::Value*)lua_touserdata(state, -2);
    Context::push(state, Meta::Value(userdata->type()));
    return 1;
}

static const luaL_Reg base_funcs[] = {{"print", luaPrint},
                                      {"plugin", luaPlugin},
                                      {"getattr", luaGet},
                                      {"gettype", luaGetType},
                                      {nullptr, nullptr}};

void* Context::luaAlloc(void* /*ud*/, void* ptr, size_t osize, size_t nsize)
{
    if(nsize)
    {
        if(osize)
        {
            return Arena::lua().realloc(ptr, nsize, 16);
        }
        else
        {
            return Arena::lua().alloc(nsize, 16);
        }
    }
    else
    {
        Arena::lua().free(ptr);
        return nullptr;
    }
}

minitl::format_buffer< 1024u > Context::getCallInfo(lua_State* state)
{
    lua_Debug   ar0, ar1;
    const char* source = "unknown source";
    const char* name   = "unknown method";
    int         line   = -1;
    if(lua_getstack(state, 0, &ar0) && lua_getinfo(state, "n", &ar0))
    {
        name = ar0.name;
    }
    if(lua_getstack(state, 1, &ar1) && lua_getinfo(state, "Sl", &ar1))
    {
        source = ar1.source;
        line   = ar1.currentline;
    }
    return minitl::format< 1024u >(FMT("{0}:{1} ({2})"), source, line, name);
}

Context::Context(const Plugin::Context& context)
    : ScriptEngine< LuaScript >(Arena::lua(), context.resourceManager)
    , m_state(lua_newstate(&Context::luaAlloc, nullptr))
{
    for(const luaL_Reg* lib = loadedlibs; lib->func; lib++)
    {
        luaL_requiref(m_state, lib->name, lib->func, 1);
        lua_pop(m_state, 1);
    }

    luaL_newmetatable(m_state, "Motor.Object");
    lua_pushstring(m_state, "__index");
    lua_pushvalue(m_state, -2);
    lua_settable(m_state, -3);
    luaL_setfuncs(m_state, s_valueMetaTable, 0);

    luaL_newmetatable(m_state, "Motor.Plugin");
    lua_pushstring(m_state, "__index");
    lua_pushvalue(m_state, -2);
    lua_settable(m_state, -3);
    luaL_setfuncs(m_state, s_pluginMetaTable, 0);

    luaL_newmetatable(m_state, "Motor.Resource");
    lua_pushstring(m_state, "__index");
    lua_pushvalue(m_state, -2);
    lua_settable(m_state, -3);
    luaL_setfuncs(m_state, s_resourceMetaTable, 0);

    luaL_newmetatable(m_state, "Motor.ResourceManager");
    lua_pushstring(m_state, "__index");
    lua_pushvalue(m_state, -2);
    lua_settable(m_state, -3);
    luaL_setfuncs(m_state, s_resourceLoaderMetaTable, 0);

    void* udata = lua_newuserdata(m_state, sizeof(weak< Resource::ResourceManager >));
    new(udata) weak< Resource::ResourceManager >(context.resourceManager);
    luaL_getmetatable(m_state, "Motor.ResourceManager");
    lua_setmetatable(m_state, -2);
    lua_setglobal(m_state, "resources");

    push(m_state, Meta::Value(motor_motor_Namespace()));
    lua_setglobal(m_state, "Motor");
    for(const luaL_Reg* method = base_funcs; method->func != nullptr; ++method)
    {
        lua_pushcfunction(m_state, method->func);
        lua_setglobal(m_state, method->name);
    }
}

Context::~Context()
{
    lua_close(m_state);
}

void Context::unload(const weak< const Resource::IDescription >& /*description*/,
                     Resource::Resource& /*handle*/)
{
}

void Context::runBuffer(const weak< const LuaScript >& script, Resource::Resource& /*resource*/,
                        const minitl::allocator::block< u8 >& buffer)
{
    int       result;
    ifilename filename = script->getScriptName();
    result
        = luaL_loadbuffer(m_state, (const char*)buffer.data(),
                          motor_checked_numcast< size_t >(buffer.count() - 1), filename.str().name);
    if(result == 0)
    {
        result = lua_pcall(m_state, 0, LUA_MULTRET, 0);
    }
    motor_assert_format(result == 0, "{0}", lua_tostring(m_state, -1));
}

void Context::reloadBuffer(const weak< const LuaScript >& script, Resource::Resource& /*resource*/,
                           const minitl::allocator::block< u8 >& buffer)
{
    int       result;
    ifilename filename = script->getScriptName();
    result
        = luaL_loadbuffer(m_state, (const char*)buffer.data(),
                          motor_checked_numcast< size_t >(buffer.count() - 1), filename.str().name);
    if(result == 0)
    {
        result = lua_pcall(m_state, 0, LUA_MULTRET, 0);
    }
    motor_assert_format(result == 0, "{0}", lua_tostring(m_state, -1));
}

}  // namespace Lua
}  // namespace Motor
