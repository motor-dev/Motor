/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CUDA_MEMORYHOST_HH_
#define MOTOR_COMPUTE_CUDA_MEMORYHOST_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class MemoryHost : public IMemoryHost
{
public:
    MemoryHost();
    ~MemoryHost();

    void release(weak< KernelScheduler::IMemoryBuffer > buffer);
};

}}}  // namespace Motor::KernelScheduler::Cuda

/**************************************************************************************************/
#endif
