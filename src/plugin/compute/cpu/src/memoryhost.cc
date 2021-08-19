/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <memoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

MemoryHost::MemoryHost() : IMemoryHost("CPU")
{
}

MemoryHost::~MemoryHost()
{
}

void MemoryHost::release(weak< KernelScheduler::IMemoryBuffer > buffer)
{
    motor_forceuse(buffer);
}

}}}  // namespace Motor::KernelScheduler::CPU
