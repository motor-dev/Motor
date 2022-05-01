/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CUDA_KERNELOBJECT_HH_
#define MOTOR_COMPUTE_CUDA_KERNELOBJECT_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class Scheduler;

class KernelObject : public minitl::refcountable
{
    friend class Scheduler;

private:
    typedef void(KernelMain)(const u32, const u32,
                             const minitl::array< weak< const IMemoryBuffer > >& params);

private:
    class Callback;

private:
    Plugin::DynamicObject m_kernel;
    KernelMain*           m_entryPoint;

public:
    KernelObject(const inamespace& name);
    ~KernelObject();
};

}}}  // namespace Motor::KernelScheduler::Cuda

/**************************************************************************************************/
#endif
