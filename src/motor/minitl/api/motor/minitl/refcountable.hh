/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/cast.hh>
#include <motor/minitl/pointer.hh>

namespace minitl {

class refcountable;

class refcountable : public pointer
{
    template < typename T >
    friend class ref;
    template < typename T >
    friend class scoped;
    template < typename T >
    friend struct formatter;

private: /* friend ref */
    mutable i_u32 m_refCount;

public:
    refcountable() : m_refCount(i_u32::create(0))
    {
    }
    inline virtual ~refcountable()
    {
        motor_assert_format(m_refCount == 0, "object is destroyed but has {0} references",
                            m_refCount);
    }

private:
    void  operator&() const;
    void* operator new(size_t size)
    {
        return ::operator new(size);
    }
    void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }

protected:
    template < typename T >
    ref< T > refFromThis()
    {
        return ref< T >(motor_checked_cast< T >(this));
    }
    template < typename T >
    ref< const T > refFromThis() const
    {
        return ref< const T >(motor_checked_cast< const T >(this));
    }
    void operator delete(void* memory)
    {
        return ::operator delete(memory);
    }
    void operator delete(void* memory, void* where)
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
