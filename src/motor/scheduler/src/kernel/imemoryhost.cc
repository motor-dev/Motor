/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler {

IMemoryHost::IMemoryHost(const istring& name) : m_name(name)
{
}

IMemoryHost::~IMemoryHost() = default;

}}  // namespace Motor::KernelScheduler
