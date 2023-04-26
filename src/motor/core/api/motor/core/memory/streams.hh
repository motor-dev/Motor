/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>

namespace Motor {

class motor_api(CORE) MemoryStream
{
private:
    minitl::allocator::block< u8 > m_memory;
    u32                            m_size;
    u32                            m_capacity;

public:
    explicit MemoryStream(minitl::allocator & allocator, u32 size = 0);
    ~MemoryStream();

    void* memory()
    {
        return m_memory;
    }
    const void* memory() const
    {
        return m_memory;
    }
    u32 size() const
    {
        return m_size;
    }
    u32 capacity() const
    {
        return m_capacity;
    }
    void resize(u32 size);
    void write(const void* buffer, u32 size);
    void erase(u32 count);
};

}  // namespace Motor
