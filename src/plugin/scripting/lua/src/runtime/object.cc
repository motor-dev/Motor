/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <stdafx.h>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <context.hh>
#include <runtime/call.hh>
#include <runtime/error.hh>
#include <runtime/object.hh>
#include <runtime/value.hh>

namespace Motor { namespace Lua {

static int pushUserdataString(lua_State* L, Meta::Value* userdata)
{
    const char* constness
        = (userdata->type().constness == Meta::Type::Const) ? "const " : "mutable ";
    const char* reference;
    const char* closing;
    switch(userdata->type().indirection)
    {
    case Meta::Type::RefPtr:
        reference = "ref<";
        closing   = ">";
        break;
    case Meta::Type::WeakPtr:
        reference = "weak<";
        closing   = ">";
        break;
    case Meta::Type::RawPtr:
        reference = "raw<";
        closing   = ">";
        break;
    case Meta::Type::Value:
        reference = "";
        constness = "";
        closing   = "";
        break;
    default:
        reference = "??? <";
        constness = "??? ";
        closing   = ">";
        break;
    }
    const char* access = (userdata->type().access == Meta::Type::Const) ? "const " : "";
    lua_pushfstring(L, "[%s%s%s%s%s object @0x%p]", constness, reference, access,
                    userdata->type().metaclass->name.c_str(), closing, userdata);
    return 1;
}

extern "C" int valueGC(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");

    Meta::Value* userdata = (Meta::Value*)lua_touserdata(state, -1);
    userdata->~Value();
    return 0;
}

extern "C" int valueToString(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");

    Meta::Value* userdata = (Meta::Value*)lua_touserdata(state, -1);
    if(userdata->type().indirection == Meta::Type::Value)
    {
        raw< const Meta::Class > metaclass = userdata->type().metaclass;
        if(metaclass == motor_class< inamespace >())
        {
            lua_pushfstring(state, "%s", userdata->as< const inamespace >().str().name);
            return 1;
        }
        if(metaclass == motor_class< istring >())
        {
            lua_pushfstring(state, "%s", userdata->as< const istring >().c_str());
            return 1;
        }
        if(metaclass == motor_class< ifilename >())
        {
            lua_pushfstring(state, "%s", userdata->as< const ifilename >().str().name);
            return 1;
        }
    }
    return pushUserdataString(state, userdata);
}

extern "C" int valueGet(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    Meta::Value*             userdata = (Meta::Value*)lua_touserdata(state, -2);
    raw< const Meta::Class > cls      = userdata->type().metaclass;

    if(cls->type() == Meta::ClassType_Array && lua_type(state, 2) == LUA_TNUMBER)
    {
        motor_assert(cls->operators,
                     "Array type %s does not implement operator methods" | cls->fullname());
        motor_assert(cls->operators->arrayOperators,
                     "Array type %s does not implement Array API methods" | cls->fullname());
        const u32 i = motor_checked_numcast< u32 >(lua_tonumber(state, 2));
        if(userdata->type().isConst())
        {
            return Context::push(state,
                                 cls->operators->arrayOperators->indexConst(*userdata, u32(i - 1)));
        }
        else
        {
            return Context::push(state,
                                 cls->operators->arrayOperators->index(*userdata, u32(i - 1)));
        }
    }
    else
    {
        Context::checkArg(state, 2, LUA_TSTRING);

        istring              name = istring(lua_tostring(state, -1));
        static const istring type = istring("__type");
        if(name == type)
        {
            Meta::Value v = Meta::Value(userdata->type());
            return Context::push(state, v);
        }
        else
        {
            Meta::Value v = (*userdata)[name];
            return Context::push(state, v);
        }
    }
}

extern "C" int valueSet(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    Meta::Value*             userdata = (Meta::Value*)lua_touserdata(state, 1);
    raw< const Meta::Class > cls      = userdata->type().metaclass;
    if(cls->type() == Meta::ClassType_Array && lua_type(state, 2) == LUA_TNUMBER)
    {
        motor_assert(cls->operators,
                     "Array type %s does not implement operator methods" | cls->fullname());
        motor_assert(cls->operators->arrayOperators,
                     "Array type %s does not implement Array API methods" | cls->fullname());
        const u32 i = motor_checked_numcast< u32 >(lua_tonumber(state, 2));
        if(userdata->type().isConst())
        {
            return Context::push(state,
                                 cls->operators->arrayOperators->indexConst(*userdata, u32(i - 1)));
        }
        else
        {
            return Context::push(state,
                                 cls->operators->arrayOperators->index(*userdata, u32(i - 1)));
        }
    }
    else
    {
        Context::checkArg(state, 2, LUA_TSTRING);

        const istring               name = istring(lua_tostring(state, -2));
        raw< const Meta::Property > p    = userdata->type().metaclass->getProperty(name);
        if(!p)
        {
            return error(state, minitl::format< 4096u >("object of type %s has no property %s")
                                    | userdata->type().name().c_str() | name.c_str());
        }
        else if(userdata->type().constness == Meta::Type::Const)
        {
            return error(state, minitl::format< 4096u >("object %s is const")
                                    | userdata->type().name().c_str());
        }
        else if(p->type.constness == Meta::Type::Const)
        {
            return error(state, minitl::format< 4096u >("property %s.%s is const")
                                    | userdata->type().name().c_str() | name.c_str());
        }
        else
        {
            Meta::Value* v      = (Meta::Value*)malloca(sizeof(Meta::Value));
            bool         result = createValue(state, -1, p->type, v);

            if(result)
            {
                p->set(*userdata, *v);
                v->~Value();
            }
            freea(v);

            if(!result)
            {
                return error(state,
                             minitl::format< 4096u >("property %s.%s has incompatible type %s")
                                 | userdata->type().name().c_str() | name.c_str()
                                 | p->type.name().c_str());
            }
        }
    }
    return 0;
}

extern "C" int valueCall(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    Meta::Value* userdata = (Meta::Value*)lua_touserdata(state, 1);
    Meta::Value  value    = (*userdata)["?call"];
    if(!value)
    {
        return error(state, minitl::format< 4096u >("object %s is not callable")
                                | userdata->type().name());
    }
    raw< const Meta::Method > method = value.as< raw< const Meta::Method > >();
    if(method)
    {
        return call(state, method);
    }
    else
    {
        return error(state, minitl::format< 4096u >("%s.?call is of type &s; expected a Method")
                                | userdata->type().name() | value.type().name());
    }
}

extern "C" int valueType(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    Meta::Value* userdata = (Meta::Value*)lua_touserdata(state, 1);
    Meta::Value  v        = Meta::Value(userdata->type());
    return Context::push(state, v);
}

const luaL_Reg s_valueMetaTable[]
    = {{"__gc", valueGC},        {"__tostring", valueToString}, {"__index", valueGet},
       {"__newindex", valueSet}, {"__call", valueCall},         {0, 0}};

}}  // namespace Motor::Lua
