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
    friend class refcountable;
    template < typename U >
    friend class ref;

private:
    T* m_ptr;

private:
    inline void swap(ref& other);

private:
    inline explicit ref(T* value);
    inline ref(T* value, Allocator& deleter);

public:
    inline ref();
    inline ref(const ref& other);
    template < typename U >
    inline ref(const ref< U >& other);  // NOLINT(google-explicit-constructor)
    template < typename U >
    inline explicit ref(scoped< U >&& other) noexcept;
    inline ref(ref&& other) noexcept;
    template < typename U >
    explicit inline ref(ref< U >&& other) noexcept;

    inline ref& operator=(const ref& other);
    template < typename U >
    inline ref& operator=(const ref< U >& other);
    inline ref& operator=(ref&& other) noexcept;
    template < typename U >
    inline ref& operator=(ref< U >&& other) noexcept;

    inline ~ref();

    inline T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
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

}  // namespace minitl

#include <motor/minitl/inl/refptr.inl>
