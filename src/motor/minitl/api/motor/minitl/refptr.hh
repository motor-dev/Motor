/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
class ref
{
    template < typename U, typename V >
    friend ref< U > motor_checked_cast(ref< V > v);
    template < typename U, typename V >
    friend ref< U > motor_const_cast(ref< V > v);
    friend class refcountable;

private:
    T* m_ptr;

private:
    inline void swap(ref& other);

private:
    inline ref(T* value);
    inline ref(T* value, Allocator& deleter);

public:
    inline ref();
    inline ref(const ref& other);
    template < typename U >
    inline ref(const ref< U > other);
    template < typename U >
    inline ref(scoped< U >&& other);

    inline ref& operator=(const ref& other);
    template < typename U >
    inline ref& operator=(const ref< U >& other);

    inline ~ref();

    inline T*   operator->() const;
    inline      operator const void*() const;
    inline bool operator!() const;
    inline T&   operator*();

    inline void clear();
    template < typename... Args >
    static inline ref< T > create(Allocator& allocator, Args&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return ref< T >(new(mem) T(minitl::forward< Args >(args)...), allocator);
    }
};

template < u16 SIZE >
class format;
template < typename T, u16 SIZE >
const format< SIZE >& operator|(const format< SIZE >& format, ref< T > t)
{
    return format | t.operator->();
}

}  // namespace minitl

#include <motor/minitl/inl/refptr.inl>
