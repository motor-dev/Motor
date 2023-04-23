/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/plugin.compute.cuda/memorybuffer.hh>
#include <memoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

MemoryBuffer::MemoryBuffer(const weak< const MemoryHost >& provider)
    : IMemoryBuffer(provider)
    , m_buffers {}
    , m_bufferCount {}
{
}

MemoryBuffer::~MemoryBuffer() = default;

}}}  // namespace Motor::KernelScheduler::Cuda
