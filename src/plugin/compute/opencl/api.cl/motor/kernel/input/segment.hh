/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_KERNEL_CL_INPUT_SEGMENT_HH_
#define MOTOR_KERNEL_CL_INPUT_SEGMENT_HH_
/**************************************************************************************************/
#include <motor/kernel/stdafx.h>

namespace Kernel {

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

}  // namespace Kernel

/**************************************************************************************************/
#endif
