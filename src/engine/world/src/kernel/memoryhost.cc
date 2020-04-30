/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#include <bugengine/world/stdafx.h>
#include <bugengine/world/kernel/memoryhost.hh>

namespace BugEngine { namespace World {

MemoryHost::MemoryHost(const SystemAllocator& pageAllocator)
    : KernelScheduler::IMemoryHost("World")
    , m_allocator(pageAllocator)
{
    be_forceuse(m_allocator);
}

MemoryHost::~MemoryHost()
{
}

void MemoryHost::release(weak< KernelScheduler::IMemoryBuffer > buffer)
{
    be_forceuse(buffer);
}

}}  // namespace BugEngine::World
