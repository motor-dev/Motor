/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <codeobject.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

KernelObject::KernelObject(const weak< const CodeObject >& code, const istring name)
    : m_kernel(
        clCreateKernel(code->m_program, minitl::format< 128u >(FMT("{0}_spir"), name), nullptr))
{
    motor_info_format(Log::opencl(), "OpenCL kernel entry point: {0}", m_kernel);
}

KernelObject::~KernelObject()
{
    clReleaseKernel(m_kernel);
}

}}}  // namespace Motor::KernelScheduler::OpenCL
