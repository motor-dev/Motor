/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/memory/streams.hh>

namespace Motor {

MemoryStream::MemoryStream(minitl::Allocator& allocator, u64 size)
    : m_memory(allocator, size)
    , m_size(size)
    , m_capacity(0)
{
}

MemoryStream::~MemoryStream()
{
}

void MemoryStream::resize(u64 size)
{
    if(!m_memory.resize(size))
    {
        m_memory.realloc(size);
    }
}

void MemoryStream::write(const void* buffer, u64 size_)
{
    if(size_ + m_size > m_capacity) resize(m_size + size_);
    memcpy(m_memory + m_size, buffer, motor_checked_numcast< size_t >(size_));
    m_size = m_size + size_;
}

void MemoryStream::erase(u64 count)
{
    motor_assert_format(m_size >= count, "erasing {0} bytes from a stream of {1} bytes", count,
                        m_size);
    m_size -= count;
}

}  // namespace Motor
