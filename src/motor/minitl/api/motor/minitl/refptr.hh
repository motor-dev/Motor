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
    inline ref(T* value, allocator& deleter);

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

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline                 operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

    inline void clear();
    template < typename... ARGS >
    static inline ref< T > create(allocator& allocator, ARGS&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return ref< T >(new(mem) T(minitl::forward< ARGS >(args)...), allocator);
    }
};

}  // namespace minitl

#include <motor/minitl/features.hh>
#include <motor/minitl/format.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif

namespace minitl {

template < typename T >
void ref< T >::swap(ref< T >& other)
{
    T* tmp_ptr  = other.operator->();
    other.m_ptr = m_ptr;
    m_ptr       = tmp_ptr;
}

template < typename T >
ref< T >::ref(T* value) : m_ptr(value)
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref(T* value, allocator& deleter) : m_ptr(value)
{
    motor_assert_format(
        value->pointer::m_allocator == 0,
        "value of type {0} already has a deleter; being refcounting multiple times?",
        typeid(T).name());
    value->pointer::m_allocator = &deleter;
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref() : m_ptr(0)
{
}

template < typename T >
ref< T >::ref(const ref& other) : m_ptr(other.operator->())
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
template < typename U >
ref< T >::ref(const ref< U >& other) : m_ptr(check_is_a< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref(ref&& other) noexcept : m_ptr(other.operator->())
{
    other.m_ptr = nullptr;
}

template < typename T >
template < typename U >
ref< T >::ref(ref< U >&& other) noexcept : m_ptr(check_is_a< T >(other.operator->()))
{
    other.m_ptr = nullptr;
}

template < typename T >
template < typename U >
ref< T >::ref(scoped< U >&& other) noexcept : m_ptr(check_is_a< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
    other.m_ptr = nullptr;
}

template < typename T >
ref< T >& ref< T >::operator=(const ref< T >& other)
{
    if(this != &other)
    {
        ref(other).swap(*this);
    }
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(const ref< U >& other)
{
    ref(other).swap(*this);
    return *this;
}

template < typename T >
ref< T >& ref< T >::operator=(ref< T >&& other) noexcept
{
    if(m_ptr) m_ptr->decref();
    m_ptr       = other.m_ptr;
    other.m_ptr = nullptr;
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(ref< U >&& other) noexcept
{
    if(m_ptr) m_ptr->decref();
    m_ptr       = check_is_a< T >(other.m_ptr);
    other.m_ptr = nullptr;
    return *this;
}

template < typename T >
ref< T >::~ref()
{
    if(m_ptr) m_ptr->decref();
}

template < typename T >
T* ref< T >::operator->() const
{
    return static_cast< T* >(m_ptr);
}

template < typename T >
ref< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool ref< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& ref< T >::operator*()
{
    return *static_cast< T* >(m_ptr);
}

template < typename T >
void ref< T >::clear()
{
    if(m_ptr) m_ptr->decref();
    m_ptr = 0;
}

template < typename T, typename U >
bool operator==(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

}  // namespace minitl
