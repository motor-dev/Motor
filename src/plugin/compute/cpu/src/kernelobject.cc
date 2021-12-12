/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <codeobject.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

KernelObject::KernelObject(weak< const CodeObject > code, const istring name)
    : m_entryPoint(
        code->m_kernel.getSymbol< KernelMain >((minitl::format< 256u >("_%s") | name).c_str()))
{
    motor_debug("[%s]: %p" | name | m_entryPoint);
}

KernelObject::~KernelObject()
{
}

void KernelObject::run(const u32 index, const u32 total)
{
    if(m_entryPoint) (*m_entryPoint)(index, total);
}

}}}  // namespace Motor::KernelScheduler::CPU
