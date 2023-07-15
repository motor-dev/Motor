/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/property.meta.hh>
#include <context.hh>
#include <runtime/value.hh>

namespace Motor { namespace Lua {

static bool convertNilToValue(lua_State* state, int index, const Meta::Type& type, void* buffer)
{
    motor_forceuse(state);
    motor_forceuse(index);
    if(type.indirection >= Meta::Type::Indirection::RawPtr)
    {
        auto* value = new(buffer) Meta::Value(type, Meta::Value::Reserve);
        *static_cast< void** >(value->memory()) = nullptr;
        return true;
    }
    else
    {
        return false;
    }
}

static bool convertStringToValue(lua_State* state, int index, const Meta::Type& type, void* buffer)
{
    raw< const Meta::InterfaceTable::TypeInterface< const char* > > charpInterface
        = type.metaclass->interfaces->charpInterface;
    if(charpInterface)
    {
        new(buffer) Meta::Value((*charpInterface->construct)(lua_tostring(state, index)));
        return true;
    }
    else
    {
        return false;
    }
}

static bool convertBooleanToValue(lua_State* state, int index, const Meta::Type& type, void* buffer)
{
    raw< const Meta::InterfaceTable::TypeInterface< bool > > boolInterface
        = type.metaclass->interfaces->boolInterface;
    if(boolInterface)
    {
        new(buffer) Meta::Value((*boolInterface->construct)(lua_toboolean(state, index)));
        return true;
    }
    else
    {
        return false;
    }
}

static bool convertNumberToValue(lua_State* state, int index, const Meta::Type& type, void* buffer)
{
    raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
        = type.metaclass->interfaces->i64Interface;
    raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
        = type.metaclass->interfaces->u64Interface;
    raw< const Meta::InterfaceTable::TypeInterface< float > > floatInterface
        = type.metaclass->interfaces->floatInterface;
    raw< const Meta::InterfaceTable::TypeInterface< double > > doubleInterface
        = type.metaclass->interfaces->doubleInterface;
    if(doubleInterface)
    {
        new(buffer) Meta::Value((*doubleInterface->construct)(lua_tonumber(state, index)));
        return true;
    }
    else if(floatInterface)
    {
        new(buffer) Meta::Value((*floatInterface->construct)(lua_tonumber(state, index)));
        return true;
    }
    if(i64Interface)
    {
        new(buffer) Meta::Value((*i64Interface->construct)(lua_tointeger(state, index)));
        return true;
    }
    else if(u64Interface)
    {
        new(buffer) Meta::Value((*u64Interface->construct)(lua_tointeger(state, index)));
        return true;
    }
    else
    {
        return false;
    }
}

static bool convertUserdataToValue(lua_State* state, int index, const Meta::Type& type,
                                   void* buffer)
{
    lua_getmetatable(state, index);
    luaL_getmetatable(state, "Motor.Object");
    if(lua_rawequal(state, -1, -2))
    {
        lua_pop(state, 2);
        auto*                userdata   = (Meta::Value*)lua_touserdata(state, index);
        Meta::ConversionCost conversion = userdata->type().calculateConversionTo(type);
        if(conversion >= Meta::ConversionCost::s_incompatible)
        {
            return false;
        }
        else
        {
            new(buffer) Meta::Value(*userdata);
            return true;
        }
    }
    else
    {
        lua_pop(state, 2);
        return true;
    }
}

static bool convertTableToValue(lua_State* state, int index, const Meta::Type& type, void* buffer)
{
    raw< const Meta::InterfaceTable::ArrayInterface > arrayInterface
        = type.metaclass->interfaces->arrayInterface;
    if(arrayInterface && arrayInterface->construct)
    {
        Meta::Type arrayType  = arrayInterface->valueType;
        u32        count      = motor_checked_numcast< u32 >(luaL_len(state, index));
        auto*      parameters = (Meta::Value*)malloca(
            minitl::align(count * sizeof(Meta::Value), motor_alignof(Meta::Value)));

        lua_pushnil(state);
        int  i      = 0;
        bool result = true;
        while(lua_next(state, index) != 0)
        {
            if(lua_type(state, -2) != LUA_TNUMBER)
            {
                lua_pop(state, 2);
                result = false;
                count  = i;
                break;
            }
            motor_assert(lua_tonumber(state, -2) == i + 1, "inconsistent LUA table");
            result |= createValue(state, -1, arrayType, &parameters[i]);
            if(!result)
            {
                lua_pop(state, 2);
                result = false;
                count  = i;
                break;
            }
            else
            {
                i++;
                lua_pop(state, 1);
            }
        }
        if(result)
        {
            Meta::Value array = (*arrayInterface->construct)(parameters, count);
            new(buffer) Meta::Value(array);
        }
        while(count)
        {
            count--;
            parameters[count].~Value();
        }
        freea(parameters);
        return result;
    }
    else
    {
        return false;
    }
}

bool createValue(lua_State* state, int index, const Meta::Type& type, void* value)
{
    int t = lua_type(state, index);
    switch(t)
    {
    case LUA_TNIL: return convertNilToValue(state, index, type, value);
    case LUA_TSTRING: return convertStringToValue(state, index, type, value);
    case LUA_TBOOLEAN: return convertBooleanToValue(state, index, type, value);
    case LUA_TNUMBER: return convertNumberToValue(state, index, type, value);
    case LUA_TUSERDATA: return convertUserdataToValue(state, index, type, value);
    case LUA_TTABLE: return convertTableToValue(state, index, type, value);
    default: return false;
    }
}

}}  // namespace Motor::Lua
