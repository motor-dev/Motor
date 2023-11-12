/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_CODEOBJECT_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_CODEOBJECT_HH

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin/dynobject.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Context;
class KernelObject;

class CodeObject : public minitl::pointer
{
    friend class KernelObject;

private:
    Plugin::DynamicObject m_kernel;
    cl_program            m_program;

private:
    cl_program loadProgram(const weak< const Context >& context);

public:
    CodeObject(const weak< const Context >& context, const inamespace& name);
    ~CodeObject() override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
