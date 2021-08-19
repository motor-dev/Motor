/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_OPENCL_CODEOBJECT_HH_
#define MOTOR_COMPUTE_OPENCL_CODEOBJECT_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin/dynobject.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Context;
class KernelObject;

class CodeObject : public minitl::refcountable
{
    friend class KernelObject;

private:
    Plugin::DynamicObject m_kernel;
    cl_program            m_program;

public:
    CodeObject(weak< const Context > context, const inamespace& name);
    ~CodeObject();
};

}}}  // namespace Motor::KernelScheduler::OpenCL

/**************************************************************************************************/
#endif
