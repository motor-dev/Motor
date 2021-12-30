/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_COMPONENTREGISTRY_META_HH_
#define MOTOR_WORLD_COMPONENTREGISTRY_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/core/memory/allocators/system.hh>

namespace Motor { namespace World {

class motor_api(WORLD) ComponentRegistry : published KernelScheduler::Producer
{
private:
    ref< KernelScheduler::Producer::Runtime > createRuntime(
        weak< const KernelScheduler::ProducerLoader > loader) const override;

public:
    class Runtime : public KernelScheduler::Producer::Runtime
    {
    private:
        SystemAllocator m_allocator4k;
        SystemAllocator m_allocator16k;
        SystemAllocator m_allocator64k;
        SystemAllocator m_allocator256k;

    public:
        Runtime(ref< Task::ITask > task, u32 parameterCount);
    };
    weak< Runtime > getRuntime(weak< const KernelScheduler::ProducerLoader > loader) const;

public:
    void addComponentStorage();

published:
    ComponentRegistry();
    ~ComponentRegistry();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
