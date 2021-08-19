/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/kernel.script.hh>

namespace Motor { namespace KernelScheduler {

Kernel::Kernel(ref< const Code > code, const istring& name) : m_kernelCode(code), m_name(name)
{
}

Kernel::~Kernel()
{
}

}}  // namespace Motor::KernelScheduler
