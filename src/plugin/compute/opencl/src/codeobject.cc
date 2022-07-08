/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <codeobject.hh>
#include <context.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

CodeObject::CodeObject(weak< const Context > context, const inamespace& name)
    : m_kernel(name, ipath("kernel"))
    , m_program(loadProgram(context))
{
}

CodeObject::~CodeObject()
{
    if(m_program) clReleaseProgram(m_program);
}

cl_program CodeObject::loadProgram(weak< const Context > context)
{
    if(m_kernel)
    {
        const char* kernelSource = *m_kernel.getSymbol< const char* >(
            istring(minitl::format< 128u >("s_clKernel%d") | context->getPointerSize()));
        const u64 kernelSourceSize = *m_kernel.getSymbol< const u64 >(
            istring(minitl::format< 128u >("s_clKernel%dSize") | context->getPointerSize()));
        return context->buildProgram(kernelSourceSize, kernelSource);
    }
    else
        return 0;
}

}}}  // namespace Motor::KernelScheduler::OpenCL
