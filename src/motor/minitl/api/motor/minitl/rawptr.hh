/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_RAWPTR_HH
#define MOTOR_MINITL_RAWPTR_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
class raw
{
public:
    T* m_ptr;

public:
    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool                  operator!() const;
    MOTOR_ALWAYS_INLINE T&       operator*();
    MOTOR_ALWAYS_INLINE const T& operator*() const;

    template < typename U >
    operator raw< U >() const  // NOLINT(google-explicit-constructor)
    {
        return {m_ptr};
    }
    T* set(T* value)
    {
        return m_ptr = value;
    }
    static inline raw< T > null();
};

}  // namespace minitl

#include <motor/minitl/inl/rawptr.hh>

#endif
