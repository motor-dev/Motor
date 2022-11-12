/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>
#include <motor/kernel/input/segment.hh>

namespace knl {

template < typename T >
struct segments
{
    int        x;
    typedef T* iterator;

    __device u32 size() const
    {
        return 0;
    }

    __device iterator begin() const
    {
        return 0;
    }
    __device iterator end() const
    {
        return 0;
    }
};

}  // namespace knl
