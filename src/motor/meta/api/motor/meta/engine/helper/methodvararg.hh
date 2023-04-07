/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

namespace Motor { namespace Meta {

template < typename T >
struct functionhelper< T, Value, Value*, u32 >
{
    enum
    {
        VarArg = 1
    };
    template < Value (*method)(Value*, u32) >
    static Value callStatic(raw< const Method > m, Value* params, u32 paramCount)
    {
        motor_forceuse(m);
        return (*method)(params, paramCount);
    }
    template < Value (T::*method)(Value*, u32) >
    static Value call(raw< const Method > m, Value* params, u32 paramCount)
    {
        motor_forceuse(m);
        if(motor_assert_format(motor_type< T* >() <= params[0].type(),
                               "expected parameter of type {0}; got {1}", motor_type< T* >().name(),
                               params[0].type().name()))
            return Value();
        return (params[0].as< T& >().*method)(params + 1, paramCount - 1);
    }
    template < Value (T::*method)(Value*, u32) const >
    static Value callConst(raw< const Method > m, Value* params, u32 paramCount)
    {
        motor_forceuse(m);
        if(motor_assert_format(motor_type< const T* >() <= params[0].type(),
                               "expected parameter of type {0}; got {1}",
                               motor_type< const T* >().name(), params[0].type().name()))
            return Value();
        return (params[0].as< const T& >().*method)(params + 1, paramCount - 1);
    }
};

}}  // namespace Motor::Meta
