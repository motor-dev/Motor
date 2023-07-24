/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_COMPONENTREGISTRY_META_HH
#define MOTOR_WORLD_COMPONENTREGISTRY_META_HH

#include <motor/world/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

#include <motor/core/memory/allocators/system.hh>

namespace Motor { namespace World {

class motor_api(WORLD) ComponentRegistry : public KernelScheduler::Producer
{
private:
    ref< KernelScheduler::Producer::Runtime > createRuntime(
        weak< const KernelScheduler::ProducerLoader > loader) const override;

public:
    class [[motor::meta(noexport)]] Runtime : public KernelScheduler::Producer::Runtime
    {
    private:
        SystemAllocator m_allocator4k;
        SystemAllocator m_allocator16k;
        SystemAllocator m_allocator64k;
        SystemAllocator m_allocator256k;

    public:
        Runtime(const ref< Task::ITask >& task, u32 parameterCount);
    };
    [[motor::meta(noexport)]] weak< Runtime > getRuntime(
        const weak< const KernelScheduler::ProducerLoader >& loader) const;

public:
    [[motor::meta(noexport)]] void addComponentStorage();

public:
    ComponentRegistry();
    ~ComponentRegistry() override;
};

}}  // namespace Motor::World

#endif
