/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <codeobject.hh>
#include <motor/scheduler/kernel/ischeduler.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

CodeObject::CodeObject(const inamespace& name) : m_kernel(name, ipath("kernel"))
{
}

CodeObject::~CodeObject()
{
}

}}}  // namespace Motor::KernelScheduler::CPU
