/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <runtime/componentregistry.meta.hh>

#include <motor/scheduler/kernel/producerloader.hh>

namespace Motor { namespace World {

ComponentRegistry::Runtime::Runtime(ref< Task::ITask > task, u32 parameterCount)
    : KernelScheduler::Producer::Runtime(task, parameterCount)
    , m_allocator4k(SystemAllocator::BlockSize_4k, 64)
    , m_allocator16k(SystemAllocator::BlockSize_16k, 8)
    , m_allocator64k(SystemAllocator::BlockSize_64k, 8)
    , m_allocator256k(SystemAllocator::BlockSize_256k, 8)
{
}

ComponentRegistry::ComponentRegistry()
{
}

ComponentRegistry::~ComponentRegistry()
{
}

ref< KernelScheduler::Producer::Runtime >
ComponentRegistry::createRuntime(weak< const KernelScheduler::ProducerLoader > loader) const
{
    ref< Runtime > result = ref< Runtime >::create(Arena::game(), loader->startTask(), 0);
    return result;
}

weak< ComponentRegistry::Runtime >
ComponentRegistry::getRuntime(weak< const KernelScheduler::ProducerLoader > loader) const
{
    return getResource(loader).getRefHandle< Runtime >();
}

}}  // namespace Motor::World
