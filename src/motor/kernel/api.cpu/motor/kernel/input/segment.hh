/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>

namespace knl {

template < typename T >
struct segment
{
private:
    T* const  m_begin;
    u32 const m_count;

public:
    segment(T* begin, T* end) : m_begin(begin), m_count(static_cast< u32 >(end - begin))
    {
    }

    typedef T* iterator;

    u32 size() const
    {
        return m_count;
    }

    iterator begin() const
    {
        return m_begin;
    }
    iterator end() const
    {
        return m_begin + m_count;
    }
};

}  // namespace knl
