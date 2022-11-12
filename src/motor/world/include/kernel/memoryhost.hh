/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/world/stdafx.h>
#include <motor/core/memory/allocators/system.hh>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace World {

class motor_api(WORLD) MemoryHost : public KernelScheduler::IMemoryHost
{
private:
    const SystemAllocator& m_allocator;

public:
    explicit MemoryHost(const SystemAllocator& pageAllocator);
    ~MemoryHost();

    void release(weak< KernelScheduler::IMemoryBuffer > buffer);
};

}}  // namespace Motor::World
