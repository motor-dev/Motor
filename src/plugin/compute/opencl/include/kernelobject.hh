/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_OPENCL_KERNELOBJECT_HH_
#define MOTOR_COMPUTE_OPENCL_KERNELOBJECT_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin.compute.opencl/scheduler.hh>
#include <motor/plugin/dynobject.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class CodeObject;

class KernelObject : public minitl::refcountable
{
private:
    cl_kernel m_kernel;

public:
    KernelObject(weak< const CodeObject > context, const istring name);
    ~KernelObject();

    void run(const minitl::array< weak< const IMemoryBuffer > >& params);
};

}}}  // namespace Motor::KernelScheduler::OpenCL

/**************************************************************************************************/
#endif
