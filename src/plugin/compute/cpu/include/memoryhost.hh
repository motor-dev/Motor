/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CPU_MEMORYHOST_HH
#define MOTOR_PLUGIN_COMPUTE_CPU_MEMORYHOST_HH

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class MemoryHost : public IMemoryHost
{
public:
    MemoryHost();
    ~MemoryHost() override = default;

    void release(const weak< KernelScheduler::IMemoryBuffer >& buffer) override;
};

}}}  // namespace Motor::KernelScheduler::CPU

#endif
