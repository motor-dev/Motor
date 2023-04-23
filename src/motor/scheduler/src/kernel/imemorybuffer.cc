/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>

namespace Motor { namespace KernelScheduler {

IMemoryBuffer::IMemoryBuffer(const weak< const IMemoryHost >& host) : m_host(host)
{
}

IMemoryBuffer::~IMemoryBuffer() = default;

}}  // namespace Motor::KernelScheduler
