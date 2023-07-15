/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_REFCOUNTABLE_HH
#define MOTOR_MINITL_REFCOUNTABLE_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/pointer.hh>

namespace minitl {

class refcountable : public pointer
{
    template < typename T >
    friend class ref;
    template < typename T >
    friend class scoped;
    template < char >
    friend struct formatter;

private: /* friend ref */
    mutable i_u32 m_refCount;

public:
    refcountable() : m_refCount(i_u32::create(0))
    {
    }
    inline ~refcountable() override
    {
        motor_assert_format(m_refCount == 0, "object is destroyed but has {0} references",
                            m_refCount);
    }

private:
    static void* operator new(size_t size)
    {
        return ::operator new(size);
    }
    static void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }

protected:
    template < typename T >
    ref< T > ref_from_this()
    {
        return ref< T >(static_cast< T* >(this));
    }
    template < typename T >
    ref< const T > ref_from_this() const
    {
        return ref< const T >(static_cast< const T* >(this));
    }
    static void operator delete(void* memory)
    {
        return ::operator delete(memory);
    }
    static void operator delete(void* memory, void* where)
    {
        ::operator delete(memory, where);
    }

public:
    inline void addref() const
    {
        ++m_refCount;
    }
    inline void decref() const
    {
        motor_assert(m_refCount > 0, "object has no reference; cannot dereference it again");
        if(!--m_refCount)
        {
            checked_delete();
        }
    }
};

}  // namespace minitl

#endif
