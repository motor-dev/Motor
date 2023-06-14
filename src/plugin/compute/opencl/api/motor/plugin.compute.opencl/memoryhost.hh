/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_MEMORYHOST_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_MEMORYHOST_HH

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class MemoryHost : public IMemoryHost
{
public:
    MemoryHost();
    ~MemoryHost() override;

    void release(const weak< KernelScheduler::IMemoryBuffer >& buffer) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
