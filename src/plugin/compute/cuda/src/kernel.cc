/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

KernelObject::KernelObject(const inamespace& name)
    : m_kernel(name, ipath("kernel"))
    , m_entryPoint(m_kernel.getSymbol< KernelMain >(istring("_kmain")))
{
    motor_debug_format(Log::cuda(), "kernel entry point: {0}", (void*)m_entryPoint);
}

KernelObject::~KernelObject() = default;

}}}  // namespace Motor::KernelScheduler::Cuda
