/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

KernelObject::KernelObject(const inamespace& name)
    : m_kernel(name, ipath("kernel"))
    , m_entryPoint(m_kernel.getSymbol< KernelMain >("_kmain"))
{
    motor_debug("kernel entry point: %p" | m_entryPoint);
}

KernelObject::~KernelObject()
{
}

}}}  // namespace Motor::KernelScheduler::Cuda
