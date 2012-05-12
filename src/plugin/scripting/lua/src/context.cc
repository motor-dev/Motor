/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>

#include    <context.h>

#include    <rtti/classinfo.script.hh>
#include    <rtti/engine/methodinfo.script.hh>


namespace BugEngine
{
namespace Lua
{

static Allocator& luaArena()
{
    return rttiArena();
}


const luaL_Reg Context::s_valueMetaTable[] = {
    {"__gc", Context::valueGC},
    {"__tostring", Context::valueToString},
    {"__index", Context::valueGet},
    {"__call", Context::valueCall},
    {0, 0}
};

static int luaPrint(lua_State *L)
{
    int n = lua_gettop(L); /* number of arguments */
    int i;
    lua_getglobal(L, "tostring");
    for (i = 1; i <= n; i++)
    {
        const char *s;
        lua_pushvalue(L, -1); /* function to be called */
        lua_pushvalue(L, i); /* value to print */
        lua_call(L, 1, 1);
        s = lua_tostring(L, -1); /* get result */
        if (s == NULL)
            return luaL_error(L, LUA_QL("tostring") " must return a string to "
                              LUA_QL("print"));
        lua_Debug ar;
        if (lua_getstack(L, 1, &ar))
        {
            lua_getinfo(L, "Snl", &ar);
            Logger::root()->log(logInfo, ar.source, ar.currentline, s);
        }
        else
        {
            be_info(s);
        }
        lua_pop(L, 1); /* pop result */
    }
    return 0;
}
static const luaL_Reg base_funcs[] = {
    {"print", luaPrint},
    {NULL, NULL}
};

void* Context::luaAlloc(void* /*ud*/, void* ptr, size_t osize, size_t nsize)
{
    if (nsize)
    {
        if (osize)
        {
            return luaArena().realloc(ptr, nsize, 16);
        }
        else
        {
            return luaArena().alloc(nsize, 16);
        }
    }
    else
    {
        luaArena().free(ptr);
        return 0;
    }
}

Context::Context(const PluginContext& context)
: ScriptEngine<LuaScript>(luaArena(), context.resourceManager)
, m_state(lua_newstate(&Context::luaAlloc, 0))
{
    luaopen_base(m_state);
    luaopen_table(m_state);
    luaopen_string(m_state);
    luaopen_math(m_state);
    luaopen_debug(m_state);

    luaL_register(m_state, "_G", base_funcs);
    luaL_register(m_state, "bugvalue", s_valueMetaTable);
}

Context::~Context()
{
    lua_close(m_state);
}

void Context::runBuffer(weak<const LuaScript> /*script*/, const Allocator::Block<u8>& block)
{
    int result;
    result = luaL_loadbuffer(m_state, (const char *) block.data(), be_checked_numcast<size_t > (block.count()), 0);
    if (result == 0)
    {
        result = lua_pcall(m_state, 0, LUA_MULTRET, 0);
    }
    be_assert(result == 0, lua_tostring(m_state, -1));
}

void Context::push(lua_State* state, const RTTI::Value& v)
{
    const RTTI::Type& t = v.type();
    if (t.metaclass == be_typeid<u8>::klass() || t.metaclass == be_typeid<u16>::klass())
    {
    }

    void* userdata = lua_newuserdata(state, sizeof (RTTI::Value));
    new(userdata) RTTI::Value(v);
    lua_getglobal(state, "bugvalue");
    lua_setmetatable(state, -2);
}

/*
void Context::push(lua_State* state, const RTTI::Value& v)
{
    switch(v.type())
    {
    case RTTI::PropertyTypeBool:
        lua_pushboolean(state, v.as<bool>());
        break;
    case RTTI::PropertyTypeInteger:
        lua_pushinteger(state, (lua_Integer)v.as<i64>());
        break;
    case RTTI::PropertyTypeUnsigned:
        lua_pushinteger(state, (lua_Integer)v.as<u64>());
        break;
    case RTTI::PropertyTypeFloat:
        lua_pushnumber(state, v.as<double>());
        break;
    case RTTI::PropertyTypeString:
        lua_pushstring(state, v.as<std::string>().c_str());
        break;
    case RTTI::PropertyTypeObject:
        push(state, v.as< ref<Object> >());
        break;
    case RTTI::PropertyTypeWeakObject:
        push(state, v.as< weak<Object> >());
        break;
    case RTTI::PropertyTypeVariant:
    case RTTI::PropertyTypeNotSet:
        be_unimplemented();
        break;
    }
}*/

RTTI::Value Context::get(lua_State *state, int index)
{
    int t = lua_type(state, index);
    switch (t)
    {
    case LUA_TSTRING:
    {
        return RTTI::Value(); //std::string(lua_tostring(state, index))
    }
    case LUA_TBOOLEAN:
    {
        return RTTI::Value(lua_toboolean(state, index)?true:false);
    }
    case LUA_TNUMBER:
    {
        return RTTI::Value(); //double(lua_tonumber(state, index)));
    }
    case LUA_TUSERDATA:
    {
        lua_getmetatable(state, index);
        lua_getglobal(state, "bugvalue");
        if (lua_rawequal(state, -1, -2))
        {
            lua_pop(state, 2);
            return *(RTTI::Value*)lua_touserdata(state, index);
        }
        else
        {
            lua_pop(state, 2);
            be_notreached();
            return RTTI::Value();
        }
    }
    default:
        return RTTI::Value();
    }
}

int Context::valueGC(lua_State *state)
{
    RTTI::Value* userdata = (RTTI::Value*)lua_touserdata(state, -1);
    userdata->~Value();
    return 0;
}

int Context::valueToString(lua_State *state)
{
    RTTI::Value* userdata = (RTTI::Value*)lua_touserdata(state, -1);
    if (userdata->type().indirection == RTTI::Type::Value)
    {
        raw<const RTTI::Class> metaclass = userdata->type().metaclass;
        if (metaclass == be_typeid< inamespace >::klass())
        {
            lua_pushfstring(state, "%s", userdata->as<const inamespace > ().str().c_str());
            return 1;
        }
        if (metaclass == be_typeid< istring >::klass())
        {
            lua_pushfstring(state, "%s", userdata->as<const istring > ().c_str());
            return 1;
        }
        if (metaclass == be_typeid< ifilename >::klass())
        {
            lua_pushfstring(state, "%s", userdata->as<const ifilename > ().str().c_str());
            return 1;
        }
    }
    lua_pushfstring(state, "[%s object @0x%p]", userdata->type().name().c_str(), userdata);
    return 1;
}

int Context::valueGet(lua_State *state)
{
    RTTI::Value* userdata = (RTTI::Value*)lua_touserdata(state, -2);
    const char *name = lua_tostring(state, -1);
    RTTI::Value v = (*userdata)[name];
    if (!v)
    {
        lua_pushnil(state);
        return 1;
    }
    push(state, v);
    return 1;
}

int Context::valueCall(lua_State *state)
{
    int top = lua_gettop(state);
    RTTI::Value* userdata = (RTTI::Value*)lua_touserdata(state, 1);

    void* v = 0;
    RTTI::Value* values = 0;
    v = malloca(be_align(sizeof (RTTI::Value), be_alignof(RTTI::Value))*(top - 1));
    values = (RTTI::Value*)v;

    for (int i = 1; i < top; i++)
    {
        new((void*) (&values[i])) RTTI::Value(get(state, i));
    }

    RTTI::Value result = (*userdata)(values, top - 1);

    for (int i = top - 1; i > 0; --i)
        values[i - 1].~Value();
    freea(v);

    if (result)
    {
        push(state, result);
        return 1;
    }
    else
    {
        return 0;
    }
}

void Context::printStack(lua_State* l)
{
    int i;
    int top = lua_gettop(l);

    be_debug("total in stack %d\n" | top);

    for (i = 1; i <= top; i++)
    {
        int t = lua_type(l, -i);
        be_debug("%d  %d  " | -i | (top - i + 1));
        switch (t)
        {
        case LUA_TSTRING:
            be_debug("string: '%s'\n" | lua_tostring(l, -i));
            break;
        case LUA_TBOOLEAN:
            be_debug("boolean %s\n" | lua_toboolean(l, -i) ? "true" : "false");
            break;
        case LUA_TNUMBER:
            be_debug("number: %g\n" | lua_tonumber(l, -i));
            break;
        case LUA_TUSERDATA:
        {
            RTTI::Value* userdata = (RTTI::Value*)lua_touserdata(l, -i);
            be_forceuse(userdata);
            be_debug("object : [%s object @0x%p]\n" | userdata->type().name().c_str() | userdata);
        }
            break;
        default:
            be_debug("%s\n" | lua_typename(l, t));
            break;
        }
    }
}

}
}
