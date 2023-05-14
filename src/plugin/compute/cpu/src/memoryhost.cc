/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <memoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

MemoryHost::MemoryHost() : IMemoryHost(istring("CPU"))
{
}

void MemoryHost::release(const weak< KernelScheduler::IMemoryBuffer >& buffer)
{
    motor_forceuse(buffer);
}

}}}  // namespace Motor::KernelScheduler::CPU
