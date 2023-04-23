/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class MemoryHost;
struct Buffer
{
    void* m_memory {};
    u32   m_size {};
};

class MemoryBuffer : public IMemoryBuffer
{
private:
    Buffer* m_buffers;
    u32     m_bufferCount;

public:
    explicit MemoryBuffer(const weak< const MemoryHost >& provider);
    ~MemoryBuffer() override;

    Buffer* buffers() const
    {
        return m_buffers;
    }
    u32 bufferCount() const
    {
        return m_bufferCount;
    }
};

}}}  // namespace Motor::KernelScheduler::CPU
