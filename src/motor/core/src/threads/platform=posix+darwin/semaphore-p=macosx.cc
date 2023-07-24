/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <motor/core/timer.hh>

#include <errno.h>
#if __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ >= 1060
#    include <dispatch/dispatch.h>
#else
#    include <CoreServices/CoreServices.h>
#endif

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data()
{
#if __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ >= 1060
    m_data.ptr = dispatch_semaphore_create(initialCount);

    if(!m_data.ptr)
    {
        motor_error_format(Log::thread(), "Could not initialize semaphore: {0}", strerror(errno));
    }
#else
    m_data.ptr = new MPSemaphoreID;
    MPCreateSemaphore(65000, initialCount, (MPSemaphoreID*)m_data.ptr);
#endif
}

Semaphore::~Semaphore() noexcept
{
#if __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ >= 1060
    dispatch_release(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr));
#else
    MPDeleteSemaphore(*(MPSemaphoreID*)m_data.ptr);
    delete(MPSemaphoreID*)m_data.ptr;
#endif
}

void Semaphore::release(int count)  // NOLINT(readability-make-member-function-const)
{
    for(int i = 0; i < count; ++i)
    {
#if __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ >= 1060
        dispatch_semaphore_signal(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr));
#else
        MPSignalSemaphore(*(MPSemaphoreID*)m_data.ptr);
#endif
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
#if __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ >= 1060
    intptr_t result = dispatch_semaphore_wait(reinterpret_cast< dispatch_semaphore_t >(m_data.ptr),
                                              DISPATCH_TIME_FOREVER);
#else
    int result;
    do
    {
        result = MPWaitOnSemaphore(*(MPSemaphoreID*)m_data.ptr, kDurationForever);
    } while(result == -1);
#endif

    if(result == 0)
    {
        return Finished;
    }
    else
    {
        motor_error_format(Log::thread(), "MPWaitOnSemaphore returned {0}", result);
        return Abandoned;
    }
}

u32 Semaphore::flushPauseCount()
{
    return 0;
}

}  // namespace Motor
