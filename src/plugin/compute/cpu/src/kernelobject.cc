/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <codeobject.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

KernelObject::KernelObject(const weak< const CodeObject >& code, const istring name)
    : IExecutor()
    , m_entryPoint(code->m_kernel.getSymbol< KernelMain >(
          istring(minitl::format< 256u >(FMT("_{0}"), name).c_str())))
{
    motor_debug_format(Log::cpu(), "[{0}]: {1}", name, (void*)m_entryPoint);
}

KernelObject::~KernelObject() = default;

void KernelObject::run(const u32 partIndex, const u32 partCount) const
{
    (*m_entryPoint)(partIndex, partCount);
}

}}}  // namespace Motor::KernelScheduler::CPU
