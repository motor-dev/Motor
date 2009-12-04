/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>

#include    <context.h>

#include    <system/filesystem.hh>
#include    <core/memory/streams.hh>
#include    <rtti/namespace.hh>


namespace BugEngine { namespace Lua
{

const luaL_Reg Context::s_refObjectMetaTable[] = {
    {"__gc",        Context::objectGC<ref>},
    {"__tostring",  Context::objectToString<ref>},
    {"__index",     Context::objectGet<ref>},
    {"__call",      Context::objectCall<ref>},
    {0, 0}
};
const luaL_Reg Context::s_weakObjectMetaTable[] = {
    {"__gc",        Context::objectGC<weak>},
    {"__tostring",  Context::objectToString<weak>},
    {"__index",     Context::objectGet<weak>},
    {"__call",      Context::objectCall<weak>},
    {0, 0}
};

static int luaPrint (lua_State *L)
{
    int n = lua_gettop(L);  /* number of arguments */
    int i;
    lua_getglobal(L, "tostring");
    for (i=1; i<=n; i++) 
    {
        const char *s;
        lua_pushvalue(L, -1);  /* function to be called */
        lua_pushvalue(L, i);   /* value to print */
        lua_call(L, 1, 1);
        s = lua_tostring(L, -1);  /* get result */
        if (s == NULL)
            return luaL_error(L, LUA_QL("tostring") " must return a string to "
                                 LUA_QL("print"));
        lua_Debug ar;
        if(lua_getstack (L, 1, &ar))
        {
            lua_getinfo(L, "Snl", &ar);
            Logger::root()->log(logInfo, ar.source, ar.currentline, s);
        }
        else
        {
            be_info(s);
        }
        lua_pop(L, 1);  /* pop result */
    }
    return 0;
}
static const luaL_Reg base_funcs[] = {
  {"print", luaPrint},
  {NULL, NULL}
};


void* Context::luaAlloc(void* ud, void* ptr, size_t osize, size_t nsize)
{
    UNUSED(ud);
    UNUSED(osize);
    if(nsize)
    {
        if(osize)
        {
            return Malloc::internalRealloc(ptr, nsize, 16);
        }
        else
        {
            return Malloc::internalAlloc(nsize, 16);
        }
    }
    else
    {
        Malloc::internalFree(ptr);
        return 0;
    }
}

Context::Context()
:   m_state(lua_newstate(&Context::luaAlloc, 0))
{
    luaopen_base(m_state);
    luaopen_table(m_state);
    luaopen_string(m_state);
    luaopen_math(m_state);
    luaopen_debug(m_state);

    luaL_register(m_state, "_G", base_funcs);
    luaL_register(m_state, "bugrefobject", s_refObjectMetaTable);
    luaL_register(m_state, "bugweakobject", s_weakObjectMetaTable);

    push(m_state, ref<Object>(RTTI::Namespace::root()));
    lua_setglobal(m_state, "BugEngine");
    lua_pop(m_state, 1);
}

Context::~Context()
{
    lua_close(m_state);
}

void Context::doFile(const char *filename)
{
    weak<BugEngine::FileSystem> fs = BugEngine::FileSystem::instance();
    ref<BugEngine::AbstractMemoryStream> file = fs->open(filename, BugEngine::eReadOnly);
    be_info("loading file %s" | filename);
    if(file)
    {
        int result;
        result = luaL_loadbuffer(m_state, (const char *)file->basememory(), (size_t)file->size(), filename);
        if(result == 0)
        {
            result = lua_pcall(m_state, 0, LUA_MULTRET, 0);
        }
        be_assert(result == 0, lua_tostring(m_state, -1));
    }
    else
    {
        printf("file not found : %s\n", filename);
    }
}

void Context::push(lua_State* state, ref<Object> o)
{
    void* userdata = lua_newuserdata(state, sizeof(ref<Object>));
    new(userdata) ref<Object>(o);
    lua_getglobal(state, "bugrefobject");
    lua_setmetatable(state, -2);
}

void Context::push(lua_State* state, weak<Object> o)
{
    void* userdata = lua_newuserdata(state, sizeof(weak<Object>));
    new(userdata) weak<Object>(o);
    lua_getglobal(state, "bugweakobject");
    lua_setmetatable(state, -2);
}

void Context::push(lua_State* state, const Value& v)
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
}

Value Context::get(lua_State *state, int index)
{
    int t = lua_type(state, index);
    switch (t)
    {
    case LUA_TSTRING:
        {
            return Value(std::string(lua_tostring(state, index)));
        }
    case LUA_TBOOLEAN:
        {
            return Value(lua_toboolean(state, index)?true:false);
        }
    case LUA_TNUMBER:
        {
            return Value(double(lua_tonumber(state, index)));
        }
    case LUA_TUSERDATA:
        {
            lua_getmetatable(state, index);
            lua_getglobal(state, "bugrefobject");
            if(lua_rawequal(state, -1, -2))
            {
                lua_pop(state, 2);
                ref<Object>* robject = (ref<Object>*)lua_touserdata(state, index);
                return Value(*robject);
            }
            lua_pop(state, 1);
            lua_getglobal(state, "bugweakobject");
            if(lua_rawequal(state, -1, -2))
            {
                lua_pop(state, 2);
                weak<Object>* wobject = (weak<Object>*)lua_touserdata(state, index);
                return Value(*wobject);
            }
            else
            {
                lua_pop(state, 2);
                be_notreached();
                return Value();
            }
        }
    default:
        return Value();
    }
}

template< template< typename > class ptr >
int Context::objectGC(lua_State *state)
{
    ptr<Object>* userdata = (ptr<Object>*)lua_touserdata(state, -1);
    userdata->~ptr<Object>();
    return 0;
}

template< template< typename > class ptr >
int Context::objectToString(lua_State *state)
{
    ptr<Object>* userdata = (ptr<Object>*)lua_touserdata(state, -1);
    lua_pushfstring(state, "[%s object @0x%p]", (*userdata)->metaclass()->name().c_str(), (*userdata).operator->());
    return 1;
}

template< template< typename > class ptr >
int Context::objectGet(lua_State *state)
{
    ptr<Object>* userdata = (ptr<Object>*)lua_touserdata(state, -2);
    if(!*userdata)
    {
        lua_pushnil(state);
        return 1;
    }
    const char *name = lua_tostring(state, -1);
    weak<const RTTI::Property> p = (*userdata)->metaclass()->getProperty(name);
    if(!p)
    {
        lua_pushnil(state);
        return 1;
    }
    Value v = p->get(*userdata);
    push(state, v);
    return 1;
}

template< template< typename > class ptr >
int Context::objectCall(lua_State *state)
{
    int i;
    int top = lua_gettop(state);
    ptr<Object>* userdata = (ptr<Object>*)lua_touserdata(state, 1);

    void* v = 0;
    Value* values = 0;
    if(top > 1)
    {
        v = malloca(sizeof(Value)*(top));
        values = new(v) Value[top-1];

        for (i = 2; i <= top; i++)
        {
            values[i-2] = get(state, i);
        }
    }
    Value result = (*userdata)->metaclass()->call(values, top-1);

    if(top-1)
    {
        ::operator delete[](values, v);
        freea(v);
    }

    if(result)
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

    printf("total in stack %d\n",top);

    for (i = 1; i <= top; i++)
    {
        int t = lua_type(l, -i);
        printf("%4d  %4d  ", -i, top-i+1);
        switch (t)
        {
        case LUA_TSTRING:
            printf("string: '%s'\n", lua_tostring(l, -i));
            break;  
        case LUA_TBOOLEAN:
            printf("boolean %s\n",lua_toboolean(l, -i) ? "true" : "false");
            break;  
        case LUA_TNUMBER:
            printf("number: %g\n", lua_tonumber(l, -i));
            break;
        case LUA_TUSERDATA:
            {
                Object** userdata = (Object**)lua_touserdata(l, -i);
                printf("object : [%s object @0x%p]\n", (*userdata)->metaclass()->name().c_str(), (*userdata));
            }
            break;
        default:
            printf("%s\n", lua_typename(l, t));
            break;
        }
    }
}

}}
