/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
        Runtime(const ref< Task::ITask >& task, u32 parameterCount);
    };
    weak< Runtime > getRuntime(const weak< const KernelScheduler::ProducerLoader >& loader) const;

public:
    void addComponentStorage();

published:
    ComponentRegistry();
    ~ComponentRegistry() override;
};

}}  // namespace Motor::World
