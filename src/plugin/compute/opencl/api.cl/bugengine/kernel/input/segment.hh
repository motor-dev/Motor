/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_KERNEL_CL_INPUT_SEGMENT_HH_
#define BE_KERNEL_CL_INPUT_SEGMENT_HH_
/**************************************************************************************************/
#include <bugengine/kernel/stdafx.h>
#include <bugengine/kernel/input/segment_part.hh>

namespace Kernel {

template < typename T >
struct segment
{
private:
    segments_part< T > m_segment;
    u32                m_current;

public:
    __device segment(__global T* begin, __global T* end) : m_segment(begin, end), m_current(0)
    {
    }
    __device segment(const segments_part< T >& s) : m_segment(s), m_current(0)
    {
    }
    __device operator __global void *() const
    {
        return reinterpret_cast< __global void* >(m_segment.m_count - m_current);
    }
    __device bool operator!() const
    {
        return m_current == m_segment.m_count;
    }
    __device segment& operator++()
    {
        m_current++;
        return *this;
    }
    __device segment& operator--()
    {
        m_current--;
        return *this;
    }
    __device segment operator++(int)
    {
        segment result = *this;
        m_current++;
        return result;
    }
    __device segment operator--(int)
    {
        segment result = *this;
        m_current--;
        return result;
    }
    __device segment& operator+=(u32 count)
    {
        m_current += count;
        return *this;
    }

    __device u32 size() const
    {
        return m_segment.m_count;
    }

    __device __global T* operator->() const
    {
        return m_segment.m_begin + m_current;
    }
    __device __global T& operator*() const
    {
        return *(m_segment.m_begin + m_current);
    }
};

}  // namespace Kernel

/**************************************************************************************************/
#endif
