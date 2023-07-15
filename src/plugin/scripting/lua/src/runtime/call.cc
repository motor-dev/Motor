/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>
#include <motor/meta/call.hh>
#include <motor/meta/conversion.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/property.meta.hh>
#include <context.hh>
#include <runtime/call.hh>
#include <runtime/error.hh>
#include <runtime/value.hh>

namespace Motor { namespace Lua {

struct LuaParameterType
{
    lua_State* state;
    int        index;
    istring    name;
    int        key;

    LuaParameterType(lua_State* state, int index) : state(state), index(index), name(""), key(-1)
    {
    }
    LuaParameterType(lua_State* state, int index, istring name, int key)
        : state(state)
        , index(index)
        , name(name)
        , key(key)
    {
    }
};

struct LuaPop
{
    lua_State* state;
    int        index;
    bool       autoPop;

    LuaPop(lua_State* state, int index, bool autoPop) : state(state), index(index), autoPop(autoPop)
    {
    }
    ~LuaPop()
    {
        if(autoPop)
        {
            lua_pop(state, 1);
        }
    }
};

Meta::ConversionCost calculateConversionTo(const LuaParameterType& type, const Meta::Type& target)
{
    int index;
    if(type.key != -1)
    {
        if(type.name.size() > 0)
        {
            lua_pushstring(type.state, type.name.c_str());
            lua_rawget(type.state, type.index);
        }
        else
        {
            lua_rawgeti(type.state, type.index, type.key);
        }
        index = -1;
    }
    else
    {
        index = type.index;
    }

    LuaPop p(type.state, index, type.key != -1);
    if(target.metaclass->interfaces->variantInterface)
    {
        switch(lua_type(type.state, index))
        {
        case LUA_TNIL:
        case LUA_TSTRING:
        case LUA_TBOOLEAN:
        case LUA_TNUMBER:
        case LUA_TUSERDATA:
        case LUA_TTABLE: return Meta::ConversionCost::s_variant;
        default: return Meta::ConversionCost::s_incompatible;
        }
    }
    else
    {
        raw< const Meta::InterfaceTable > interfaces = target.metaclass->interfaces;
        switch(lua_type(type.state, index))
        {
        case LUA_TNIL:
            return target.indirection >= Meta::Type::Indirection::RawPtr
                       ? Meta::ConversionCost()
                       : Meta::ConversionCost::s_incompatible;
        case LUA_TSTRING:
            return interfaces->charpInterface ? Meta::ConversionCost()
                                              : Meta::ConversionCost::s_incompatible;
        case LUA_TBOOLEAN:
            return interfaces->boolInterface ? Meta::ConversionCost()
                                             : Meta::ConversionCost::s_incompatible;
        case LUA_TNUMBER:
            return interfaces->doubleInterface
                       ? Meta::ConversionCost()
                       : (interfaces->floatInterface ? Meta::ConversionCost(0, 1)
                                                     : Meta::ConversionCost::s_incompatible);
        case LUA_TUSERDATA:
            lua_getmetatable(type.state, index);
            luaL_getmetatable(type.state, "Motor.Object");
            if(lua_rawequal(type.state, -1, -2))
            {
                lua_pop(type.state, 2);
                auto* userdata = (Meta::Value*)lua_touserdata(type.state, index);
                return userdata->type().calculateConversionTo(target);
            }
            else
            {
                lua_pop(type.state, 2);
                return Meta::ConversionCost::s_incompatible;
            }
        case LUA_TTABLE:
            if(interfaces->arrayInterface)
            {
                const Meta::Type&    valueType = interfaces->arrayInterface->valueType;
                Meta::ConversionCost c;
                lua_pushnil(type.state);
                while(lua_next(type.state, index < 0 ? index - 1 : index))
                {
                    int keyType = lua_type(type.state, -2);
                    if(keyType != LUA_TNUMBER)
                    {
                        lua_pop(type.state, 2);
                        return Meta::ConversionCost::s_incompatible;
                    }
                    else
                    {
                        c += calculateConversionTo(LuaParameterType(type.state, -1), valueType);
                        lua_pop(type.state, 1);
                        if(c >= Meta::ConversionCost::s_incompatible) return c;
                    }
                }
                return c;
            }
            else
            {
                return Meta::ConversionCost::s_incompatible;
            }
        default: return Meta::ConversionCost::s_incompatible;
        }
    }
}

void convert(const LuaParameterType& type, void* buffer, const Meta::Type& target)
{
    int index;
    if(type.key != -1)
    {
        if(type.name.size() > 0)
        {
            lua_pushstring(type.state, type.name.c_str());
            lua_rawget(type.state, type.index);
        }
        else
        {
            lua_rawgeti(type.state, type.index, type.key);
        }
        index = -1;
    }
    else
    {
        index = type.index;
    }
    LuaPop p(type.state, index, type.key != -1);
    bool   result = createValue(type.state, index, target, buffer);
    motor_assert_format(result, "could not convert lua value {0} to {1}",
                        Context::tostring(type.state, index), target);
    motor_forceuse(result);
}

typedef Meta::ArgInfo< LuaParameterType > LuaParameterInfo;

int call(lua_State* state, raw< const Meta::Method > method)
{
    int nargs = lua_gettop(state) - 1;
    if((nargs == 1 && lua_type(state, 2) == LUA_TTABLE)
       || (nargs == 2 && lua_type(state, 3) == LUA_TTABLE))
    {
        bool error          = false;
        u32  parameterCount = 0;
        lua_pushnil(state);
        for(; lua_next(state, nargs + 1); ++parameterCount)
        {
            lua_pop(state, 1);
        }
        u32   positionParameterCount = 0;
        u32   keywordParameterCount  = 0;
        auto* parameters
            = (LuaParameterInfo*)malloca(sizeof(LuaParameterInfo) * (parameterCount + 1));

        if(nargs == 2)
        {
            new(&parameters[positionParameterCount++])
                LuaParameterInfo(LuaParameterType(state, nargs));
            parameterCount++;
        }
        lua_pushnil(state);
        while(!error && lua_next(state, nargs + 1))
        {
            /* removes value */
            lua_pop(state, 1);
            switch(lua_type(state, -1))
            {
            case LUA_TNUMBER:
            {
                int j = (int)lua_tonumber(state, -1);
                new(&parameters[positionParameterCount])
                    LuaParameterInfo(LuaParameterType(state, nargs + 1, istring(), j));
                positionParameterCount++;
            }
            break;
            case LUA_TSTRING:
            {
                const char* keyStr = lua_tostring(state, -1);
                auto        key    = istring(keyStr);
                keywordParameterCount++;
                new(&parameters[parameterCount - keywordParameterCount])
                    LuaParameterInfo(key, LuaParameterType(state, nargs + 1, key, 0));
            }
            break;
            default:
                lua_pop(state, 1);
                error = true;
                break;
            }
        }
        if(!error)
        {
            Meta::CallInfo result = Meta::resolve< LuaParameterType >(
                method, {parameters, positionParameterCount},
                {parameters + positionParameterCount, keywordParameterCount});
            if(result.conversion < Meta::ConversionCost::s_incompatible)
            {
                Meta::Value v = Meta::call< LuaParameterType >(
                    method, result, {parameters, positionParameterCount},
                    {parameters + positionParameterCount, keywordParameterCount});
                freea(parameters);
                return Context::push(state, v);
            }
            else
            {
                freea(parameters);
            }
        }
        else
        {
            freea(parameters);
        }
    }
    auto* parameters = (LuaParameterInfo*)malloca(sizeof(LuaParameterInfo) * (nargs + 1));
    for(int i = 0; i < nargs; ++i)
    {
        new(&parameters[i]) LuaParameterInfo(LuaParameterType(state, 2 + i));
    }
    Meta::CallInfo result = Meta::resolve< LuaParameterType >(
        method, {parameters, parameters + nargs}, {nullptr, nullptr});
    if(result.conversion < Meta::ConversionCost::s_incompatible)
    {
        Meta::Value v = Meta::call< LuaParameterType >(
            method, result, {parameters, parameters + nargs}, {nullptr, nullptr});
        freea(parameters);
        return Context::push(state, v);
    }
    else
    {
        freea(parameters);
        char message[4096] = "no overload can convert all parameters\n  ";
        for(int i = 0; i < nargs; ++i)
        {
            strcat(message, minitl::format< 128u >(FMT("{0}{1}"), Context::tostring(state, 2 + i),
                                                   (i < nargs - 1 ? ", " : "")));
        }
        return error(state, message);
    }
}
}}  // namespace Motor::Lua
