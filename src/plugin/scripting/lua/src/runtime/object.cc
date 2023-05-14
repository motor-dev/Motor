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
    lua_pushstring(L, minitl::format<>(FMT("[{0} object {1}]"), userdata->type(), userdata));
    return 1;
}

static int valueGC(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");

    auto* userdata = (Meta::Value*)lua_touserdata(state, -1);
    userdata->~Value();
    return 0;
}

static int valueToString(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");

    auto* userdata = (Meta::Value*)lua_touserdata(state, -1);
    if(userdata->type().indirection == Meta::Type::Indirection::Value)
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
    pushUserdataString(state, userdata);
    return 1;
}

static int valueGet(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    auto*                    userdata = (Meta::Value*)lua_touserdata(state, -2);
    raw< const Meta::Class > cls      = userdata->type().metaclass;

    if(cls->type() == Meta::ClassType_Array && lua_type(state, 2) == LUA_TNUMBER)
    {
        motor_assert_format(cls->operators, "Array type {0} does not implement operator methods",
                            cls->fullname());
        motor_assert_format(cls->operators->arrayOperators,
                            "Array type {0} does not implement Array API methods", cls->fullname());
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

        auto                 name = istring(lua_tostring(state, -1));
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

static int valueSet(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    auto*                    userdata = (Meta::Value*)lua_touserdata(state, 1);
    raw< const Meta::Class > cls      = userdata->type().metaclass;
    if(cls->type() == Meta::ClassType_Array && lua_type(state, 2) == LUA_TNUMBER)
    {
        motor_assert_format(cls->operators, "Array type {0} does not implement operator methods",
                            cls->fullname());
        motor_assert_format(cls->operators->arrayOperators,
                            "Array type {0} does not implement Array API methods", cls->fullname());
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
            return error(state,
                         minitl::format< 4096u >(FMT("object of type {0} has no property {1}"),
                                                 userdata->type(), name));
        }
        else if(userdata->type().constness == Meta::Type::Constness::Const)
        {
            return error(state,
                         minitl::format< 4096u >(FMT("object {0} is const"), userdata->type()));
        }
        else if(p->type.constness == Meta::Type::Constness::Const)
        {
            return error(state, minitl::format< 4096u >(FMT("property {0}.{1} is const"),
                                                        userdata->type(), name));
        }
        else
        {
            auto* v      = (Meta::Value*)malloca(sizeof(Meta::Value));
            bool  result = createValue(state, -1, p->type, v);

            if(result)
            {
                p->set(*userdata, *v);
                v->~Value();
            }
            freea(v);

            if(!result)
            {
                return error(state, minitl::format< 4096u >(
                                        FMT("property {0}.{1} has incompatible type {2}"),
                                        userdata->type(), name, p->type));
            }
        }
    }
    return 0;
}

static int valueCall(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    auto*       userdata = (Meta::Value*)lua_touserdata(state, 1);
    Meta::Value value    = (*userdata)[Meta::Class::nameOperatorCall()];
    if(!value)
    {
        return error(state,
                     minitl::format< 4096u >(FMT("object {0} is not callable"), userdata->type()));
    }
    auto method = value.as< raw< const Meta::Method > >();
    if(method)
    {
        return call(state, method);
    }
    else
    {
        return error(state,
                     minitl::format< 4096u >(FMT("{0}.?call is of type {1}; expected a Method"),
                                             userdata->type(), value.type()));
    }
}

static int valueType(lua_State* state)
{
    Context::checkArg(state, 1, "Motor.Object");
    auto*       userdata = (Meta::Value*)lua_touserdata(state, 1);
    Meta::Value v        = Meta::Value(userdata->type());
    return Context::push(state, v);
}

const luaL_Reg s_valueMetaTable[]
    = {{"__gc", valueGC},        {"__tostring", valueToString}, {"__index", valueGet},
       {"__newindex", valueSet}, {"__call", valueCall},         {"typeof", valueType},
       {nullptr, nullptr}};

}}  // namespace Motor::Lua
