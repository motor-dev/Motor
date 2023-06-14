/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_MEMORYHOST_HH
#define MOTOR_WORLD_MEMORYHOST_HH

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
    ~MemoryHost() override;

    void release(const weak< KernelScheduler::IMemoryBuffer >& buffer) override;
};

}}  // namespace Motor::World

#endif
