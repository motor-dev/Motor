/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <memoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

MemoryHost::MemoryHost() : IMemoryHost("Cuda")
{
}

MemoryHost::~MemoryHost() = default;

void MemoryHost::release(const weak< KernelScheduler::IMemoryBuffer >& buffer)
{
    motor_forceuse(buffer);
}

}}}  // namespace Motor::KernelScheduler::Cuda
