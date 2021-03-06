/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <taskscheduler.hh>

#include <settings.meta.hh>
#include <taskitem.hh>

#include <motor/core/environment.hh>
#include <motor/core/threads/threadlocal.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace Task {

static tls< TaskScheduler::Worker > s_worker;

static const u32 s_maxConcurrentTasks = 4096;
static const u32 s_breakdownPerThread = 4;

static inline u32 nextPowerOf2(u32 number)
{
    u32 result = s_maxConcurrentTasks * s_breakdownPerThread;
    while(result < number)
        result <<= 1;
    return result;
}

TaskScheduler::TaskPool::TaskPool(u32 workerCount)
    : m_workerCount(workerCount)
    , m_poolSignal(0)
    , m_poolLock(workerCount)
    , m_taskPool(static_cast< TaskItem** >(Arena::task().alloc(
          nextPowerOf2(s_maxConcurrentTasks * s_breakdownPerThread * m_workerCount)
          * sizeof(TaskItem*))))
    , m_firstQueued(i_u32::create(0))
    , m_lastQueued(i_u32::create(0))
    , m_firstFree(i_u32::create(0))
    , m_poolMask(nextPowerOf2(s_maxConcurrentTasks * s_breakdownPerThread * m_workerCount) - 1)
{
}

TaskScheduler::TaskPool::~TaskPool()
{
    Arena::task().free(m_taskPool);
}

void TaskScheduler::TaskPool::push(TaskItem* item, u32 count)
{
    /* In this method, beware of overflows! */
    u32 poolStart  = m_firstFree.addExchange(count);
    u32 poolEnd    = poolStart + count;
    u32 bufferSize = m_poolMask + 1;

    while(poolEnd - m_firstQueued > bufferSize)
        motor_pause();

    for(u32 i = 0; i < count; ++i)
    {
        m_taskPool[(i + poolStart) & m_poolMask] = item;
    }

    while(m_lastQueued != poolStart)
        motor_pause();
    m_lastQueued.set(poolEnd);
    m_poolSignal.release(count);
}

TaskItem* TaskScheduler::TaskPool::pop()
{
    u32 index = m_firstQueued.addExchange(1);
    return m_taskPool[index & m_poolMask];
}

void TaskScheduler::TaskPool::resize(u32 workerCount)
{
    motor_assert(m_workerCount != 0, "%d is not a valid worker count" | workerCount);
    if(!s_worker) m_poolLock.wait();
    for(u32 i = 1; i < m_workerCount; ++i)
        m_poolLock.wait();

    /* exclusive access to buffer */
    /* do resizing */

    if(s_worker)
        m_poolLock.release(workerCount - 1);
    else
        m_poolLock.release(workerCount);
}

class TaskScheduler::Worker
{
    MOTOR_NOCOPY(Worker);

private:
    Thread m_workThread;

public:
    Worker(weak< TaskScheduler > scheduler, size_t workerId);
    ~Worker();

    bool doWork(const weak< TaskScheduler >& sc);

    static intptr_t work(intptr_t p1, intptr_t p2);
};

TaskScheduler::Worker::Worker(weak< TaskScheduler > scheduler, size_t workerId)
    : m_workThread(istring(minitl::format< 128u >("worker %u") | workerId),
                   &TaskScheduler::Worker::work, reinterpret_cast< intptr_t >(this),
                   reinterpret_cast< intptr_t >(scheduler.operator->()), Thread::BelowNormal)
{
}

TaskScheduler::Worker::~Worker()
{
}

bool TaskScheduler::Worker::doWork(const weak< TaskScheduler >& sc)
{
    TaskItem* item = sc->m_workerTaskPool.pop();

    if(item)
    {
        u32       index = item->m_started++;
        const u32 total = item->m_total;
        item->m_executor->run(index, total);
        if(++item->m_finished != total)
        {
            return false;
        }
        else
        {
            item->m_owner->completed(sc->m_scheduler);
            sc->m_taskItemPool.release(item);
            sc->m_taskItemAvailable.release(1);
            return sc->taskDone();
        }
    }
    else
        return true;
}

intptr_t TaskScheduler::Worker::work(intptr_t p1, intptr_t p2)
{
    Worker* w         = reinterpret_cast< Worker* >(p1);
    s_worker          = w;
    TaskScheduler* sc = reinterpret_cast< TaskScheduler* >(p2);
    while(sc->isRunning())
    {
        if(sc->m_workerTaskPool.m_poolSignal.wait() == Threads::Waitable::Finished)
        {
            sc->m_workerTaskPool.m_poolLock.wait();
            bool end = w->doWork(sc);
            sc->m_workerTaskPool.m_poolLock.release(1);
            if(end)
            {
                sc->notifyEnd();
            }
        }
    }
    return 0;
}

TaskScheduler::TaskScheduler(weak< Scheduler > scheduler)
    : m_workers(Arena::task())
    , m_scheduler(scheduler)
    , m_workerCount(i_u32::create(
          SchedulerSettings::Scheduler::get().ThreadCount > 0
              ? SchedulerSettings::Scheduler::get().ThreadCount
              : size_t(minitl::max(1, i32(Environment::getEnvironment().getProcessorCount())))))
    , m_mainThreadPool(1)
    , m_workerTaskPool(m_workerCount)
    , m_taskItemPool(Arena::task(), s_maxConcurrentTasks)
    , m_taskItemAvailable(s_maxConcurrentTasks)
{
    motor_info("initializing scheduler with %d workers" | m_workerCount);
    for(size_t i = 0; i < m_workerCount; ++i)
    {
        m_workers.push_back(new Worker(this, i));
    }
}

TaskScheduler::~TaskScheduler()
{
    m_workerTaskPool.push(0, static_cast< u32 >(m_workers.size()));
    for(size_t i = 0; i < m_workers.size(); ++i)
        delete m_workers[i];
}

void TaskScheduler::queue(weak< const ITask > task, weak< const IExecutor > executor,
                          u32 breakdownCount)
{
    m_scheduler->m_runningTasks++;
    m_taskItemAvailable.wait();
    TaskItem* item = m_taskItemPool.allocate(task, executor, breakdownCount);

    if(task->affinity == Scheduler::WorkerThread)
    {
        m_workerTaskPool.push(item, breakdownCount);
    }
    else
    {
        m_mainThreadPool.push(item, breakdownCount);
    }
}

void TaskScheduler::mainThreadJoin()
{
    while(true)
    {
        if(m_mainThreadPool.m_poolSignal.wait() == Threads::Waitable::Finished)
        {
            TaskItem* item = m_mainThreadPool.pop();

            if(item)
            {
                u32 index = item->m_started++;
                item->m_executor->run(index, item->m_total);
                if(taskDone())
                {
                    m_taskItemPool.release(item);
                    break;
                }
            }
            else
                break;
        }
    }
}

bool TaskScheduler::taskDone()
{
    if(0 == --m_scheduler->m_runningTasks)
    {
        motor_info("No task left; exiting");
        return true;
    }
    else
        return false;
}

void TaskScheduler::notifyEnd()
{
    m_mainThreadPool.push(0, 1);
}

bool TaskScheduler::isRunning() const
{
    return m_scheduler->m_running;
}

}}  // namespace Motor::Task
