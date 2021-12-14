/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <codeloader.hh>
#include <kernelloader.hh>
#include <memoryhost.hh>
#include <scheduler.hh>

#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/kernel/ischeduler.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/scheduler/task/kerneltask.hh>
#include <motor/scheduler/task/task.hh>
#include <kernel_optims.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CPUKernelTaskItem;

class CPUTaskItem : public Task::ITaskItem
{
private:
    CPUKernelTaskItem* m_kernelItem;
    u32                m_index;
    u32                m_total;

public:
    virtual void run(weak< Motor::Scheduler > sc) override;

    CPUTaskItem(CPUKernelTaskItem* item, u32 index, u32 total);
};

class CPUKernelTaskItem
{
    friend class Scheduler;

private:
    weak< Task::KernelTask > m_owner;
    weak< Scheduler >        m_cpuScheduler;
    weak< KernelObject >     m_object;
    const u32                m_jobCount;
    i_u32                    m_doneCount;

public:
    CPUKernelTaskItem(weak< Task::KernelTask > owner, weak< Scheduler > scheduler,
                      weak< KernelObject > object, u32 parameterCount, u32 jobCount);
    ~CPUKernelTaskItem();

    void onJobCompleted(weak< Motor::Scheduler > sc);

    weak< Task::KernelTask > owner() const
    {
        return m_owner;
    }
    weak< KernelObject > object() const
    {
        return m_object;
    }

    CPUTaskItem* items()
    {
        u8* buffer = reinterpret_cast< u8* >(this);
        return reinterpret_cast< CPUTaskItem* >(buffer + sizeof(*this));
    }
};

CPUTaskItem::CPUTaskItem(CPUKernelTaskItem* item, u32 index, u32 total)
    : ITaskItem(item->owner())
    , m_kernelItem(item)
    , m_index(index)
    , m_total(total)
{
}

CPUKernelTaskItem::CPUKernelTaskItem(weak< Task::KernelTask > owner, weak< Scheduler > scheduler,
                                     weak< KernelObject > object, u32 parameterCount, u32 jobCount)
    : m_owner(owner)
    , m_cpuScheduler(scheduler)
    , m_object(object)
    , m_jobCount(jobCount)
    , m_doneCount(i_u32::create(0))
{
    motor_forceuse(parameterCount);
    CPUTaskItem* item       = 0;
    CPUTaskItem* itemBuffer = items();
    for(u32 i = 0; i < m_jobCount; ++i)
    {
        CPUTaskItem* newItem = &itemBuffer[i];
        new(newItem) CPUTaskItem(this, i, jobCount);
        newItem->next = item;
        item          = newItem;
    }
}

CPUKernelTaskItem::~CPUKernelTaskItem()
{
    CPUTaskItem* itemBuffer = items();
    for(u32 i = 0; i < m_jobCount; ++i)
    {
        itemBuffer[m_jobCount - i - 1].~CPUTaskItem();
    }
}

void CPUKernelTaskItem::onJobCompleted(weak< Motor::Scheduler > sc)
{
    if(++m_doneCount == m_jobCount)
    {
        CPUTaskItem* item       = 0;
        CPUTaskItem* itemBuffer = items();
        for(u32 i = 0; i < m_jobCount; ++i)
        {
            CPUTaskItem* newItem = &itemBuffer[i];
            newItem->next        = item;
            item                 = newItem;
        }
        m_doneCount = 0;
        m_owner->completed(sc);
    }
}

void CPUTaskItem::run(weak< Motor::Scheduler > sc)
{
    m_kernelItem->object()->run(m_index, m_total);
    m_kernelItem->onJobCompleted(sc);
}

Scheduler::Scheduler(const Plugin::Context& context)
    : IScheduler("CPU", context.scheduler, CPUType)
    , m_resourceManager(context.resourceManager)
    , m_cpuLoaders(Arena::task(), s_cpuVariantCount + 1)
    , m_memoryHost(scoped< MemoryHost >::create(Arena::task()))
{
    for(i32 i = 0; i < s_cpuVariantCount; ++i)
    {
        if(*s_cpuVariants[i])
            motor_info("registering optimised CPU kernel loader for %s" | s_cpuVariants[i]);
        else
            motor_info("registering unoptimised CPU kernel loader");
        ref< CodeLoader > codeLoader
            = ref< CodeLoader >::create(Arena::task(), inamespace(s_cpuVariants[i]));
        m_cpuLoaders.push_back(ref< KernelLoader >::create(Arena::task(), codeLoader));
        m_resourceManager->attach< Code >(codeLoader);
        m_resourceManager->attach< Kernel >(m_cpuLoaders[i]);
    }
}

Scheduler::~Scheduler()
{
    for(minitl::vector< ref< KernelLoader > >::const_reverse_iterator it = m_cpuLoaders.rbegin();
        it != m_cpuLoaders.rend(); ++it)
    {
        m_resourceManager->detach< Kernel >(*it);
        m_resourceManager->detach< Code >((*it)->codeLoader());
    }
}

void Scheduler::run(weak< Task::KernelTask > task)
{
    /* TODO: set option to use Neon/AVX/SSE */
    const u32          jobCount = m_scheduler->workerCount() * 4;
    CPUKernelTaskItem* item     = reinterpret_cast< CPUKernelTaskItem* >(task->schedulerData(this));
    CPUTaskItem*       items    = item->items();
    m_scheduler->queueTasks(&items[jobCount - 1], &items[0], jobCount);
}

void* Scheduler::createData(weak< Task::KernelTask > task, u32 parameterCount)
{
    weak< const Kernel > kernel = task->kernel();
    weak< KernelObject > object
        = kernel->getResource(m_cpuLoaders[0]).getRefHandle< KernelObject >();
    const u32          jobCount = m_scheduler->workerCount() * 4;
    CPUKernelTaskItem* item
        = new(Arena::task().alloc(sizeof(CPUKernelTaskItem) + jobCount * sizeof(CPUTaskItem)))
            CPUKernelTaskItem(task, this, object, parameterCount, jobCount);
    return item;
}

void Scheduler::disposeData(void* data)
{
    reinterpret_cast< CPUKernelTaskItem* >(data)->~CPUKernelTaskItem();
    Arena::task().free(data);
}

}}}  // namespace Motor::KernelScheduler::CPU
