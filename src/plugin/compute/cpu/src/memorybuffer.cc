/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <memoryhost.hh>
#include <motor/plugin.compute.cpu/memorybuffer.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

MemoryBuffer::MemoryBuffer(weak< const MemoryHost > provider) : IMemoryBuffer(provider)
{
}

MemoryBuffer::~MemoryBuffer()
{
}

}}}  // namespace Motor::KernelScheduler::CPU
