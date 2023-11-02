/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_KERNELOBJECT_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_KERNELOBJECT_HH

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
    KernelObject(const weak< const CodeObject >& code, istring name);
    ~KernelObject() override;

    // void run(const minitl::vector< weak< const IMemoryBuffer > >& params);
};

}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
