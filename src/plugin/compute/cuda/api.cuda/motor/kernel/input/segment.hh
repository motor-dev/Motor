/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_INPUT_SEGMENT_HH
#define MOTOR_KERNEL_INPUT_SEGMENT_HH

#include    <motor/kernel/stdafx.h>


namespace knl
{

template < typename T >
struct segment
{
private:
    T*  const   m_begin;
    u32 const   m_count;

public:
    __device segment(T* begin, T* end)
        :   m_begin(begin)
        ,   m_count(static_cast<u32>(end - begin))
    {
    }

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


}

#endif
