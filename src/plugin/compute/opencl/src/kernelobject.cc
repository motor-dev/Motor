/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <codeobject.hh>
#include <kernelobject.hh>
#include <motor/scheduler/kernel/ischeduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

KernelObject::KernelObject(weak< const CodeObject > code, const istring name)
    : m_kernel(clCreateKernel(code->m_program, (minitl::format< 128u >("%s_spir") | name), 0))
{
    motor_info("OpenCL kernel entry point: %p" | m_kernel);
}

KernelObject::~KernelObject()
{
    clReleaseKernel(m_kernel);
}

}}}  // namespace Motor::KernelScheduler::OpenCL
