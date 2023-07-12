/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_CALL_HH
#define MOTOR_META_CALL_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/conversion.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/value.hh>
#include <motor/minitl/span.hh>
#include <motor/minitl/view.hh>

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
CallInfo getCost(raw< const Method::Overload > overload, minitl::span< u32 > argumentIndices,
                 minitl::view< ArgInfo< T > > arguments,
                 minitl::view< ArgInfo< T > > namedArguments)
{
    const u32 argumentCount      = arguments.size();
    const u32 namedArgumentCount = namedArguments.size();
    CallInfo  result             = {ConversionCost::s_incompatible, overload, 0, 0};
    if(namedArgumentCount > overload->parameters.size())
    {
        /* too many arguments */
        return result;
    }
    ConversionCost cost;
    u32            placedArgumentCount = overload->parameters.size() - namedArgumentCount;
    if(placedArgumentCount > argumentCount) placedArgumentCount = argumentCount;
    u32 variadicArgumentCount = argumentCount - placedArgumentCount;
    if(variadicArgumentCount)
    {
        if(!overload->variadic)
        {
            /* too many arguments */
            return result;
        }
        cost += Meta::ConversionCost::s_variant;
        result.variadicCount = variadicArgumentCount;
    }

    const Method::Parameter* const begin = overload->parameters.begin();
    const Method::Parameter*       p     = begin;
    for(u32 i = 0; i < placedArgumentCount; ++i, ++p)
    {
        cost += calculateConversionTo(arguments[i].type, p->type);
        if(cost >= ConversionCost::s_incompatible) return result;
    }

    u32          remainingParamCount = overload->parameters.size() - placedArgumentCount;
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
                cost += calculateConversionTo(namedArguments[i].type, namedParams[j]->type);
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
    result.defaultValuesCount
        = overload->parameters.size() - placedArgumentCount - namedArgumentCount;
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
CallInfo resolve(raw< const Method > method, minitl::view< ArgInfo< T > > arguments,
                 minitl::span< ArgInfo< T > > namedArguments)
{
    const u32           namedArgumentCount = namedArguments.size();
    u32*                indices = (u32*)malloca(sizeof(u32) * 2 * (namedArgumentCount + 1));
    minitl::span< u32 > indexSpans[2]
        = {{indices, indices + namedArgumentCount + 1},
           {indices + namedArgumentCount + 1, indices + 2 * namedArgumentCount + 2}};
    u32      indexTmp  = 0;
    u32      indexBest = 1;
    CallInfo best      = {ConversionCost::s_incompatible, {nullptr}, 0, 0};
    for(const auto& overload: method->overloads)
    {
        CallInfo c = getCost< T >({&overload}, indexSpans[indexTmp], arguments, namedArguments);
        if(c.conversion < best.conversion)
        {
            best = c;
            indexTmp ^= 1;
            indexBest ^= 1;
        }
    }
    for(u32 i = 0; i < namedArgumentCount; ++i)
    {
        namedArguments[i].parameter = indexSpans[indexBest][i];
    }
    minitl::sort(namedArguments.begin(), namedArguments.end(), ArgumentSort< T >());
    freea(indices[1]);
    freea(indices[0]);
    return best;
}

template < typename T >
Value call(raw< const Method > method, CallInfo callInfo, minitl::view< ArgInfo< T > > arguments,
           minitl::view< ArgInfo< T > > namedArguments)
{
    const u32 argumentCount       = arguments.size();
    const u32 namedArgumentCount  = namedArguments.size();
    const u32 totalParameterCount = callInfo.overload->parameters.size() + callInfo.variadicCount;
    auto*     v                   = (Value*)malloca(sizeof(Value) * totalParameterCount);
    const Method::Parameter* const begin = callInfo.overload->parameters.begin();
    const Method::Parameter*       p     = begin;
    for(u32 i = 0; i < argumentCount - callInfo.variadicCount; ++i, ++p)
    {
        motor_assert(p != callInfo.overload->parameters.end(), "too many arguments passed to call");
        convert(arguments[i].type, static_cast< void* >(&v[i]), p->type);
    }
    u32 index = argumentCount;
    for(u32 i = 0; i < namedArgumentCount; ++i, ++p, ++index)
    {
        for(; namedArguments[i].parameter != index; ++index, ++p)
        {
            motor_assert(p != callInfo.overload->parameters.end(),
                         "too many arguments passed to call");
            motor_assert_format(*(p->defaultValue), "Parameter {0} does not have a default value",
                                p->name);
            new(static_cast< void* >(&v[index])) Value(Value::ByRef(*(p->defaultValue)));
        }
        motor_assert_format(p->name == namedArguments[i].name,
                            "Argument mismatch: {0} expected, got {1}", p->name,
                            namedArguments[i].name);
        motor_assert(p != callInfo.overload->parameters.end(), "too many arguments passed to call");
        convert(namedArguments[i].type, static_cast< void* >(&v[index]), p->type);
    }
    for(; p != callInfo.overload->parameters.end(); ++p, ++index)
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
