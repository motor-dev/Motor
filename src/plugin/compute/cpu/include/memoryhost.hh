/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class MemoryHost : public IMemoryHost
{
public:
    MemoryHost();
    ~MemoryHost();

    void release(weak< KernelScheduler::IMemoryBuffer > buffer);
};

}}}  // namespace Motor::KernelScheduler::CPU
