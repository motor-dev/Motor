/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>

namespace Motor { namespace KernelScheduler {

Kernel::Kernel(const ref< const Code >& code, const istring& name)
    : m_kernelCode(code)
    , m_name(name)
{
}

Kernel::~Kernel() = default;

}}  // namespace Motor::KernelScheduler
