/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_HELPER_METHOD_HH_
#define MOTOR_META_ENGINE_HELPER_METHOD_HH_
/**************************************************************************************************/
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

class Value;
struct Method;

template < typename T >
static inline Value call(raw< const Method > method, Value& _this, Value* params, u32 paramCount)
{
    motor_forceuse(method);
    return _this.as< const T& >()(params, paramCount);
}

template < typename T >
struct wrap
{
    static inline void copy(const void* src, void* dst)
    {
        new(dst) T(*(T*)src);
    }

    static inline void destroy(void* src)
    {
        motor_forceuse(src);
        ((T*)src)->~T();
    }
};

template < typename T, u32 Count >
struct wrap< T[Count] >
{
    typedef T ArrayType[Count];

    static inline void copy(const void* src, void* dst)
    {
        for(u32 i = 0; i < Count; ++i)
            new(&static_cast< T* >(dst)[i]) T(static_cast< const T* >(src)[i]);
    }

    static inline void destroy(void* src)
    {
        for(u32 i = 0; i < Count; ++i)
            static_cast< const T* >(src)[i].~T();
    }
};

template < size_t size >
inline void nullconstructor(const void* src, void* dst)
{
    memcpy(dst, src, size);
}

template <>
inline void nullconstructor< 0 >(const void* /*src*/, void* /*dst*/)
{
}

static inline void nulldestructor(void*)
{
}

template < typename T >
static Value createPod(raw< const Method > method, Value* params, u32 paramCount)
{
    motor_forceuse(method);
    motor_forceuse(params);
    motor_forceuse(paramCount);
    motor_assert(paramCount == 0, "too many parameters to POD construction");
    return Value(motor_type< T >(), Value::Reserve);
}

template < typename T >
static Value createPodCopy(raw< const Method > method, Value* params, u32 paramCount)
{
    motor_forceuse(method);
    motor_forceuse(paramCount);
    motor_assert(paramCount == 1, "invalid parameter count to POD copy");
    return params[0];
}

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
