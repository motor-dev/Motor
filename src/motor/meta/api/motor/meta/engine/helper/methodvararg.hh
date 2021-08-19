/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_HELPER_METHODVARARG_HH_
#define MOTOR_META_ENGINE_HELPER_METHODVARARG_HH_
/**************************************************************************************************/

namespace Motor { namespace Meta {

template < typename T >
struct functionhelper< T, Value, Value*, u32 >
{
    enum
    {
        VarArg = 1
    };
    template < Value (*method)(Value*, u32) >
    static Value callStatic(Value* params, u32 paramCount)
    {
        return (*method)(params, paramCount);
    }
    template < Value (T::*method)(Value*, u32) >
    static Value call(Value* params, u32 paramCount)
    {
        motor_assert_recover(motor_type< T* >() <= params[0].type(),
                             "expected parameter of type %s; got %s" | motor_type< T* >().name()
                                 | params[0].type().name(),
                             return Value());
        return (params[0].as< T& >().*method)(params + 1, paramCount - 1);
    }
    template < Value (T::*method)(Value*, u32) const >
    static Value callConst(Value* params, u32 paramCount)
    {
        motor_assert_recover(motor_type< const T* >() <= params[0].type(),
                             "expected parameter of type %s; got %s"
                                 | motor_type< const T* >().name() | params[0].type().name(),
                             return Value());
        return (params[0].as< const T& >().*method)(params + 1, paramCount - 1);
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
