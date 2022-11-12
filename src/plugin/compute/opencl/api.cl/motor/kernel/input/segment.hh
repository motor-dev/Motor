/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>

namespace knl {
template < typename T >
struct segment
{
    T* const  m_begin;
    u32 const m_count;

    typedef T* iterator;

    __device u32 size() const
    {
        return m_count;
    }

    __device iterator begin() const
    {
        return m_begin;
    }
    __device iterator end() const
    {
        return m_begin + m_count;
    }
};

}  // namespace knl
