/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <memoryhost.hh>
#include <motor/plugin.compute.cuda/memorybuffer.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

MemoryBuffer::MemoryBuffer(weak< const MemoryHost > provider) : IMemoryBuffer(provider)
{
}

MemoryBuffer::~MemoryBuffer()
{
}

}}}  // namespace Motor::KernelScheduler::Cuda
