/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>
#include <objc/objc.h>

#define USE_DISPATCH_SEMAPHORE (__ENVIRONMENT_IPHONE_OS_VERSION_MIN_REQUIRED__ >= 50000)
#if USE_DISPATCH_SEMAPHORE
#    include <dispatch/dispatch.h>
#else
#    include <semaphore.h>
#endif
#include <errno.h>
#include <stdio.h>

namespace Motor {

#if !USE_DISPATCH_SEMAPHORE
static int x;
#endif

Semaphore::Semaphore(int initialCount)
{
#if USE_DISPATCH_SEMAPHORE
    m_data.ptr = dispatch_semaphore_create(initialCount);
    if(!m_data.ptr)
#else
    m_data.ptr = sem_open(minitl::format< 1024u >("/motor_%s") | x++, O_CREAT, 0644, 65535);
    if(reinterpret_cast< sem_t* >(m_data.ptr) == SEM_FAILED)
#endif
    {
        motor_error("Could not initialize semaphore: %s" | strerror(errno));
    }
#if !USE_DISPATCH_SEMAPHORE
    release(initialCount);
#endif
}

Semaphore::~Semaphore()
{
#if USE_DISPATCH_SEMAPHORE
    dispatch_release(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr));
#else
    sem_close(reinterpret_cast< sem_t* >(m_data.ptr));
#endif
}

void Semaphore::release(int count)
{
    for(int i = 0; i < count; ++i)
    {
#if USE_DISPATCH_SEMAPHORE
        dispatch_semaphore_signal(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr));
#else
        sem_post(reinterpret_cast< sem_t* >(m_data.ptr));
#endif
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
#if USE_DISPATCH_SEMAPHORE
    int result = dispatch_semaphore_wait(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr),
                                         DISPATCH_TIME_FOREVER);
#else
    int result = sem_wait(reinterpret_cast< sem_t* >(m_data.ptr));
#endif
    if(result == 0)
    {
        return Finished;
    }
    else
    {
        motor_error("Could not wait on semaphore: %s" | strerror(errno));
        motor_notreached();
        return Abandoned;
    }
}

}  // namespace Motor
