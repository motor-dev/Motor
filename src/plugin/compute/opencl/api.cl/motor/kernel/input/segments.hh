/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_COMPUTE_INPUT_SEGMENTS_HH
#define MOTOR_KERNEL_COMPUTE_INPUT_SEGMENTS_HH

#include <motor/kernel/stdafx.h>
#include <motor/kernel/input/segment.hh>

namespace knl {

template < typename T >
struct segments
{
    int        x {};
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

#endif
