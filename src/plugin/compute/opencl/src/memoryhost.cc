/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin.compute.opencl/memoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

MemoryHost::MemoryHost() : IMemoryHost("OpenCL")
{
}

MemoryHost::~MemoryHost()
{
}

void MemoryHost::release(weak< KernelScheduler::IMemoryBuffer > buffer)
{
    motor_forceuse(buffer);
}

}}}  // namespace Motor::KernelScheduler::OpenCL
