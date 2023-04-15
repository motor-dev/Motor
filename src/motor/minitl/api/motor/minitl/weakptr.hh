/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/scopedptr.hh>

namespace minitl {

template < typename T >
class weak
{
    template < typename U, typename V >
    friend weak< U > motor_checked_cast(weak< V > v);

private:
    T* m_ptr;

private:
    inline void swap(weak& other);

public:
    inline weak();
    inline weak(T* p);                      // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(ref< U > other);            // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(const scoped< U >& other);  // NOLINT(google-explicit-constructor)
    inline weak(const weak& other);
    template < typename U >
    inline weak(const weak< U >& other);  // NOLINT(google-explicit-constructor)
    inline ~weak();

    inline weak& operator=(const weak& other);
    template < typename U >
    inline weak& operator=(const weak< U >& other);
    template < typename U >
    inline weak& operator=(U* other);

    inline T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool operator!() const;
    inline T&   operator*();

    inline void clear();
};

template < typename T >
struct hash< weak< T > >
{
    u32 operator()(weak< T > t)
    {
        return hash< T* >()(t.operator->());
    }
    bool operator()(weak< T > t1, weak< T > t2)
    {
        return hash< T* >()(t1.operator->(), t2.operator->());
    }
};

}  // namespace minitl

#include <motor/minitl/inl/weakptr.inl>
