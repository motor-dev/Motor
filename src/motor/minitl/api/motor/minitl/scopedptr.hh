/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
class scoped
{
    template < typename U >
    friend class scoped;
    template < typename U >
    friend class ref;

private:
    T* m_ptr;

private:
    scoped(T* value, allocator& allocator);

public:
    scoped(const scoped& other) = delete;
    template < typename U >
    inline scoped(const scoped< U >& other) = delete;
    template < typename U >
    scoped& operator=(const scoped< U >& other) = delete;
    scoped& operator=(const scoped& other)      = delete;
    inline scoped();
    inline ~scoped();
    inline scoped(scoped&& other) noexcept;
    template < typename U >
    inline scoped(scoped< U >&& other);  // NOLINT(google-explicit-constructor)

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline                 operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

    template < typename U >
    inline void reset(scoped< U >&& other);

    template < typename... ARGS >
    static inline scoped< T > create(allocator& allocator, ARGS&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return scoped< T >(new(mem) T(minitl::forward< ARGS >(args)...), allocator);
    }
};

}  // namespace minitl

#include <motor/minitl/features.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif

namespace minitl {

template < typename T >
scoped< T >::scoped(T* value, allocator& allocator) : m_ptr(value)
{
    motor_assert_format(
        value->pointer::m_allocator == 0,
        "value of type {0} already has a deleter; being refcounting multiple times?",
        typeid(T).name());
    value->pointer::m_allocator = &allocator;
}

template < typename T >
scoped< T >::scoped() : m_ptr(0)
{
}

template < typename T >
scoped< T >::~scoped()
{
    if(m_ptr) m_ptr->checked_delete();
}

template < typename T >
scoped< T >::scoped(scoped&& other) noexcept : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
scoped< T >::scoped(scoped< U >&& other) : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
void scoped< T >::reset(scoped< U >&& other)
{
    if(m_ptr != other.m_ptr)
    {
        if(m_ptr)
        {
            m_ptr->checked_delete();
        }
        m_ptr       = other.m_ptr;
        other.m_ptr = 0;
    }
}

template < typename T >
T* scoped< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
scoped< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool scoped< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& scoped< T >::operator*()
{
    return *m_ptr;
}

template < typename T, typename U >
bool operator==(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

}  // namespace minitl
