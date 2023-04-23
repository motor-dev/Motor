/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <kernel/memoryhost.hh>

namespace Motor { namespace World {

MemoryHost::MemoryHost(const SystemAllocator& pageAllocator)
    : KernelScheduler::IMemoryHost("World")
    , m_allocator(pageAllocator)
{
    motor_forceuse(m_allocator);
}

MemoryHost::~MemoryHost() = default;

void MemoryHost::release(const weak< KernelScheduler::IMemoryBuffer >& buffer)
{
    motor_forceuse(buffer);
}

}}  // namespace Motor::World
