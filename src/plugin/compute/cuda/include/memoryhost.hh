/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class MemoryHost : public IMemoryHost
{
public:
    MemoryHost();
    ~MemoryHost() override;

    void release(const weak< KernelScheduler::IMemoryBuffer >& buffer) override;
};

}}}  // namespace Motor::KernelScheduler::Cuda
