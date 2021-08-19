/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <codeobject.hh>
#include <context.hh>
#include <motor/scheduler/kernel/ischeduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

CodeObject::CodeObject(weak< const Context > context, const inamespace& name)
    : m_kernel(name, ipath("kernel"))
{
    const char* kernelSource = *m_kernel.getSymbol< const char* >(
        istring(minitl::format< 128u >("s_clKernel%d") | context->getPointerSize()));
    const u64 kernelSourceSize = *m_kernel.getSymbol< const u64 >(
        istring(minitl::format< 128u >("s_clKernel%dSize") | context->getPointerSize()));
    m_program = context->buildProgram(kernelSourceSize, kernelSource);
}

CodeObject::~CodeObject()
{
    clReleaseProgram(m_program);
}

}}}  // namespace Motor::KernelScheduler::OpenCL
