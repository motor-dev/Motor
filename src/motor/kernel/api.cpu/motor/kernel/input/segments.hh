/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_INPUT_SEGMENTS_HH
#define MOTOR_KERNEL_INPUT_SEGMENTS_HH

#include <motor/kernel/stdafx.h>
#include <motor/kernel/input/segment.hh>

namespace knl {

template < typename T >
struct segments
{
private:
    segment< T >* const m_segments;
    u32 const           m_segmentCount;
    u32 const           m_elementCount;

public:
    segments(segment< T >* parts, u32 segmentCount, u32 count)
        : m_segments(parts)
        , m_segmentCount(segmentCount)
        , m_elementCount(count)
    {
    }

    struct iterator
    {
        friend struct segments;

    private:
        segment< T >* m_currentSegment;
        u32           m_currentOffset;

    private:
        iterator(segment< T >* segment, u32 offset)
            : m_currentSegment(segment)
            , m_currentOffset(offset)
        {
        }

    public:
        bool operator==(const iterator& other) const
        {
            return m_currentSegment == other.m_currentSegment
                   && m_currentOffset == other.m_currentOffset;
        }
        bool operator!=(const iterator& other) const
        {
            return m_currentSegment != other.m_currentSegment
                   || m_currentOffset != other.m_currentOffset;
        }
        iterator& operator++()
        {
            if(++m_currentOffset == m_currentSegment->size())
            {
                m_currentOffset = 0;
                m_currentSegment++;
            }
            return *this;
        }

        iterator& operator--()
        {
            if(m_currentOffset == 0)
            {
                --m_currentSegment;
                m_currentOffset = m_currentSegment->size() - 1;
            }
            return *this;
        }

        const iterator operator++(int)  // NOLINT(readability-const-return-type)
        {
            iterator result = *this;
            ++m_currentOffset;
            while(m_currentOffset == m_currentSegment->size())
            {
                m_currentOffset = 0;
                m_currentSegment++;
            }
            return result;
        }

        const iterator operator--(int)  // NOLINT(readability-const-return-type)
        {
            iterator result = *this;
            --m_currentSegment;
            while(m_currentOffset == (u32)-1)
            {
                m_currentOffset = m_currentSegment->size() - 1;
            }
            return result;
        }

        iterator& operator+=(u32 count)
        {
            while(count)
            {
                if(m_currentOffset + count >= m_currentSegment->size())
                {
                    u32 progress = m_currentSegment->size() - m_currentOffset;
                    count -= progress;
                    ++m_currentSegment;
                    m_currentOffset = 0;
                }
            }
            return *this;
        }

        iterator operator+(u32 count)
        {
            iterator result = *this;
            result += count;
            return result;
        }

        iterator operator-(u32 count)
        {
            iterator result = *this;
            result -= count;
            return result;
        }

        T* operator->() const
        {
            return m_currentSegment->begin() + m_currentOffset;
        }

        T& operator*() const
        {
            return *(m_currentSegment->begin() + m_currentOffset);
        }
    };

    u32 size() const
    {
        return m_elementCount;
    }

    iterator begin() const
    {
        return iterator(m_segments, 0);
    }
    iterator end() const
    {
        segment< T >* last_segment = m_segments + m_segmentCount;
        return iterator(last_segment, 0);
    }
};

}  // namespace knl

#endif
