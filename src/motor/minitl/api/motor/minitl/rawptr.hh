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
    inline T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool     operator!() const;
    inline T&       operator*();
    inline const T& operator*() const;

    template < typename U >
    operator raw< U >() const  // NOLINT(google-explicit-constructor)
    {
        raw< U > result = {m_ptr};
        return result;
    }
    T* set(T* value)
    {
        return m_ptr = value;
    }
    static inline raw< T > null();
};

}  // namespace minitl

#include <motor/minitl/inl/rawptr.inl>
