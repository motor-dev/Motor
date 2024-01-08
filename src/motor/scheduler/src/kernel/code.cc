/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/code.meta.hh>

namespace Motor { namespace KernelScheduler {

Code::Code(inamespace name) : m_name(minitl::move(name))
{
}

Code::~Code() = default;

}}  // namespace Motor::KernelScheduler
