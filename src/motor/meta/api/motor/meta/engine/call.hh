/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_ENGINE_CALL_HH
#define MOTOR_META_ENGINE_CALL_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/conversion.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

struct CallInfo
{
    ConversionCost                conversion {};
    raw< const Method::Overload > overload {};
    u32                           variadicCount {};
    u32                           defaultValuesCount {};

    bool operator<(const CallInfo& other) const
    {
        return conversion < other.conversion;
    }
};

template < typename T >
struct ArgInfo
{
    istring name;
    u32     parameter;
    T       type;
    ArgInfo() : name(), parameter(0), type()
    {
    }
    explicit ArgInfo(const T& t) : name(), parameter(0), type(t)
    {
    }
    ArgInfo(istring name, const T& t) : name(name), parameter(0), type(t)
    {
    }
};

template < typename T >
CallInfo getCost(raw< const Method::Overload > overload, u32 argumentIndices[],
                 const ArgInfo< T > arguments[], u32 argumentCount,
                 const ArgInfo< T > namedArguments[] = 0, u32 namedArgumentCount = 0)
{
    CallInfo result = {ConversionCost::s_incompatible, overload, 0, 0};
    if(namedArgumentCount > overload->params.count)
    {
        /* too many arguments */
        return result;
    }
    ConversionCost cost;
    u32            placedArgumentCount = overload->params.count - namedArgumentCount;
    if(placedArgumentCount > argumentCount) placedArgumentCount = argumentCount;
    u32 variadicArgumentCount = argumentCount - placedArgumentCount;
    if(variadicArgumentCount)
    {
        if(!overload->vararg)
        {
            /* too many arguments */
            return result;
        }
        cost += Meta::ConversionCost::s_variant;
        result.variadicCount = variadicArgumentCount;
    }

    const Method::Parameter* const begin = overload->params.begin();
    const Method::Parameter*       p     = begin;
    for(u32 i = 0; i < placedArgumentCount; ++i, ++p)
    {
        cost += calculateConversion(arguments[i].type, p->type);
        if(cost >= ConversionCost::s_incompatible) return result;
    }

    u32          remainingParamCount = overload->params.count - placedArgumentCount;
    size_t       s                   = sizeof(raw< const Method::Parameter >) * remainingParamCount;
    const auto** namedParams         = (const Method::Parameter**)malloca(s);
    for(u32 i = 0; i < remainingParamCount; ++i)
        namedParams[i] = begin + placedArgumentCount + i;
    for(u32 i = 0; i < namedArgumentCount; ++i)
    {
        bool found = false;
        for(u32 j = i; j < remainingParamCount; ++j)
        {
            if(namedParams[j]->name == namedArguments[i].name)
            {
                cost += calculateConversion(namedArguments[i].type, namedParams[j]->type);
                found = true;
                minitl::swap(namedParams[j], namedParams[i]);
                argumentIndices[i] = (u32)(namedParams[i] - begin);
                break;
            }
        }
        if(!found)
        {
            // named param not in list
            cost = ConversionCost::s_incompatible;
            break;
        }
    }
    result.defaultValuesCount = overload->params.count - placedArgumentCount - namedArgumentCount;
    for(u32 i = 0; i < remainingParamCount - namedArgumentCount; ++i)
    {
        if(!namedParams[namedArgumentCount + i]->defaultValue.operator*())
        {
            /* no default value */
            cost = ConversionCost::s_incompatible;
            break;
        }
    }
    freea(namedParams);
    result.conversion = cost;
    return result;
}

template < typename T >
struct ArgumentSort
{
    bool operator()(const ArgInfo< T >& arg1, const ArgInfo< T >& arg2) const
    {
        return arg1.parameter < arg2.parameter;
    }
};

template < typename T >
CallInfo resolve(raw< const Method > method, ArgInfo< T > arguments[], u32 argumentCount,
                 ArgInfo< T > namedArguments[] = 0, u32 namedArgumentCount = 0)
{
    u32*     indices[2] = {(u32*)malloca(sizeof(u32) * (namedArgumentCount + 1)),
                           (u32*)malloca(sizeof(u32) * (namedArgumentCount + 1))};
    u32      indexTmp   = 0;
    u32      indexBest  = 1;
    CallInfo best       = {ConversionCost::s_incompatible, {nullptr}, 0, 0};
    for(u32 i = 0; i < method->overloads.count; ++i)
    {
        raw< const Method::Overload > overload = {method->overloads.begin() + i};
        CallInfo c = getCost(overload, indices[indexTmp], arguments, argumentCount, namedArguments,
                             namedArgumentCount);
        if(c.conversion < best.conversion)
        {
            best = c;
            indexTmp ^= 1;
            indexBest ^= 1;
        }
    }
    for(u32 i = 0; i < namedArgumentCount; ++i)
    {
        namedArguments[i].parameter = indices[indexBest][i];
    }
    minitl::sort(namedArguments, namedArguments + namedArgumentCount, ArgumentSort< T >());
    freea(indices[1]);
    freea(indices[0]);
    return best;
}

template < typename T >
Value call(raw< const Method > method, CallInfo callInfo, const ArgInfo< T > arguments[],
           u32 argumentCount, const ArgInfo< T > namedArguments[] = 0, u32 namedArgumentCount = 0)
{
    const u32 totalParameterCount        = callInfo.overload->params.count + callInfo.variadicCount;
    auto*     v                          = (Value*)malloca(sizeof(Value) * totalParameterCount);
    const Method::Parameter* const begin = callInfo.overload->params.begin();
    const Method::Parameter*       p     = begin;
    for(u32 i = 0; i < argumentCount - callInfo.variadicCount; ++i, ++p)
    {
        motor_assert(p != callInfo.overload->params.end(), "too many arguments passed to call");
        convert(arguments[i].type, static_cast< void* >(&v[i]), p->type);
    }
    u32 index = argumentCount;
    for(u32 i = 0; i < namedArgumentCount; ++i, ++p, ++index)
    {
        for(; namedArguments[i].parameter != index; ++index, ++p)
        {
            motor_assert(p != callInfo.overload->params.end(), "too many arguments passed to call");
            motor_assert_format(*(p->defaultValue), "Parameter {0} does not have a default value",
                                p->name);
            new(static_cast< void* >(&v[index])) Value(Value::ByRef(*(p->defaultValue)));
        }
        motor_assert_format(p->name == namedArguments[i].name,
                            "Argument mismatch: {0} expected, got {1}", p->name,
                            namedArguments[i].name);
        motor_assert(p != callInfo.overload->params.end(), "too many arguments passed to call");
        convert(namedArguments[i].type, static_cast< void* >(&v[index]), p->type);
    }
    for(; p != callInfo.overload->params.end(); ++p, ++index)
    {
        motor_assert_format(p->defaultValue, "Parameter {0} does not have a default value",
                            p->name);
        new(static_cast< void* >(&v[index])) Value(Value::ByRef(*(p->defaultValue)));
    }
    for(u32 i = argumentCount - callInfo.variadicCount; i < argumentCount; ++i, ++index)
    {
        convert(namedArguments[i].type, static_cast< void* >(&v[index]), p->type);
    }
    Value result = callInfo.overload->call(method, v, totalParameterCount);
    for(u32 i = totalParameterCount; i > 0; --i)
    {
        v[i - 1].~Value();
    }
    freea(v);
    return result;
}

}}  // namespace Motor::Meta

#endif
