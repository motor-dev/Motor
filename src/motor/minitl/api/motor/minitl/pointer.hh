/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_POINTER_HH
#define MOTOR_MINITL_POINTER_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/allocator.hh>
#include <motor/minitl/assert.hh>

namespace minitl {

template < typename U, typename T >
static inline U* check_is_a(T* t)
{
    return t;
}

template < typename T >
static inline void checked_destroy(const T* ptr)
{
    static_assert(sizeof(T) >= sizeof(char), "type must be complete");
    if(ptr)
    {
        ptr->~T();
    }
}

template < typename T >
class ref;
template < typename T >
class weak;
template < typename T >
class scoped;
class Arena;

class pointer
{
    template < typename T >
    friend class ref;
    template < typename T >
    friend class weak;
    template < typename T >
    friend class scoped;
    template < char >
    friend struct formatter;

private:
    mutable allocator* m_allocator;
#if MOTOR_ENABLE_WEAKCHECK
    mutable i_u32 m_weakCount;
#endif
public:
    pointer()
        : m_allocator(nullptr)
#if MOTOR_ENABLE_WEAKCHECK
        , m_weakCount(i_u32::create(0))
#endif
    {
    }
    inline virtual ~pointer()
    {
#if MOTOR_ENABLE_WEAKCHECK
        motor_assert_format(m_weakCount == 0, "object is destroyed but has {0} weak references",
                            m_weakCount);
#endif
    }

protected:
    static void* operator new(size_t size)
    {
        return ::operator new(size);
    }
    static void operator delete(void* memory)
    {
        return ::operator delete(memory);
    }
    static void operator delete(void* memory, void* where)
    {
        ::operator delete(memory, where);
    }

public:  // entity behavior
    pointer(const pointer& other)            = delete;
    pointer& operator=(const pointer& other) = delete;
    pointer(pointer&& other)                 = delete;
    pointer& operator=(pointer&& other)      = delete;
    void     operator&() const               = delete;  // NOLINT(google-runtime-operator)

private:                                                // friend scoped/ref
    static void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }

protected:
    inline void checked_delete() const
    {
        allocator* d = m_allocator;
        checked_destroy(this);
        d->free(this);
    }
#if MOTOR_ENABLE_WEAKCHECK
    inline void add_weak() const
    {
        ++m_weakCount;
    }
    inline void dec_weak() const
    {
        motor_assert(m_weakCount, "object has no weak reference; cannot dereference it again");
        --m_weakCount;
    }
#endif
};

}  // namespace minitl

#endif
