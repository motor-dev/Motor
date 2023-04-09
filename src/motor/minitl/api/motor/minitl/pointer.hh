/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_POINTER_HH_
#define MOTOR_MINITL_POINTER_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/allocator.hh>

namespace minitl {

template < typename U, typename T >
static inline U* checkIsA(T* t)
{
    return t;
}

template < typename T >
static inline void checked_destroy(const T* ptr)
{
    char typeMustBeComplete[sizeof(T)];
    (void)typeMustBeComplete;
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
    mutable Allocator* m_allocator;
#if MOTOR_ENABLE_WEAKCHECK
    mutable i_u32 m_weakCount;
#endif
public:
    pointer()
        : m_allocator(0)
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

public:
    void operator delete(void* memory)
    {
        return ::operator delete(memory);
    }
    void operator delete(void* memory, void* where)
    {
        ::operator delete(memory, where);
    }

private:  // entity behavior
    pointer(const pointer& other)            = delete;
    pointer& operator=(const pointer& other) = delete;
    void     operator&() const               = delete;
    void*    operator new(size_t size)       = delete;

private:  // friend scopedptr/refptr
    void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }

protected:
    inline void checked_delete() const
    {
        Allocator* d = m_allocator;
        checked_destroy(this);
        d->free(this);
    }
#if MOTOR_ENABLE_WEAKCHECK
    inline void addweak() const
    {
        ++m_weakCount;
    }
    inline void decweak() const
    {
        motor_assert(m_weakCount, "object has no weak reference; cannot dereference it again");
        --m_weakCount;
    }
#endif
};

}  // namespace minitl

/**************************************************************************************************/
#endif
