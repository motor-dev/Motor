/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
class raw
{
public:
    T* m_ptr;

public:
    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline                 operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();
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

template < typename T >
T* raw< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
raw< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool raw< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& raw< T >::operator*()
{
    return *m_ptr;
}

template < typename T >
const T& raw< T >::operator*() const
{
    return *m_ptr;
}

template < typename T >
raw< T > raw< T >::null()
{
    raw< T > result = {0};
    return result;
}

}  // namespace minitl
