/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <errno.h>
#include <stdio.h>

#if defined(__linux)
#    include <limits.h>
#    include <linux/futex.h>
#    include <sys/syscall.h>
#    include <unistd.h>

namespace Motor {

static i_u32 s_pauseCount;

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.value.set(initialCount);
}

Semaphore::~Semaphore() noexcept
{
    syscall(SYS_futex, &m_data.value, FUTEX_WAKE_PRIVATE, INT_MAX);
}

void Semaphore::release(int count)
{
    m_data.value += count;
    if(syscall(SYS_futex, &m_data.value, FUTEX_WAKE_PRIVATE, count) < 0)
    {
        motor_error_format(Log::thread(), "Semaphore error: {0}[{1}]", errno, strerror(errno));
        motor_notreached();
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    long result;
    do
    {
        i32 count = m_data.value--;
        if(count >= 1)
        {
            return Waitable::Finished;
        }
        ++m_data.value;
        ++s_pauseCount;
        result = syscall(SYS_futex, &m_data.value, FUTEX_WAIT_PRIVATE, count, NULL);
    } while(result == 0 || errno == EAGAIN);

    motor_error_format(Log::thread(), "Semaphore error: {0}-{1}[{2}]", result, errno,
                       strerror(errno));
    motor_notreached();
    return Abandoned;
}

u32 Semaphore::flushPauseCount()
{
    return s_pauseCount.exchange(0);
}

}  // namespace Motor

#elif defined(__FreeBSD__)

#    include <limits.h>
#    include <sys/types.h>
#    include <sys/umtx.h>

namespace Motor {

static i_u32 s_pauseCount;

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.value.set(initialCount);
}

Semaphore::~Semaphore() noexcept
{
    _umtx_op(&m_data.value, UMTX_OP_WAKE, INT_MAX, nullptr, nullptr);
}

void Semaphore::release(int count)
{
    m_data.value += count;
    _umtx_op(&m_data.value, UMTX_OP_WAKE, count, nullptr, nullptr);
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    int result;
    do
    {
        i32 count = m_data.value--;
        if(count >= 1)
        {
            return Waitable::Finished;
        }
        ++m_data.value;
        ++s_pauseCount;
        result = _umtx_op(&m_data.value, UMTX_OP_WAIT, count, nullptr, nullptr);
    } while(result == 0 || errno == EINTR);

    motor_error_format(Log::thread(), "Semaphore error: {0}-{1}[{2}]", result, errno,
                       strerror(errno));
    motor_notreached();
    return Abandoned;
}

u32 Semaphore::flushPauseCount()
{
    return s_pauseCount.exchange(0);
}

}  // namespace Motor

#else

#    include <semaphore.h>

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.ptr = new sem_t;
    if(sem_init(reinterpret_cast< sem_t* >(m_data.ptr), 0, initialCount) != 0)
    {
        motor_error_format(Log::thread(), "Could not initialize semaphore: {0}", strerror(errno));
    }
}

Semaphore::~Semaphore() noexcept
{
    if(sem_destroy(reinterpret_cast< sem_t* >(m_data.ptr)) != 0)
    {
        motor_error_format(Log::thread(), "Could not destroy semaphore: {0}", strerror(errno));
    }
    delete reinterpret_cast< sem_t* >(m_data.ptr);
}

void Semaphore::release(int count)
{
    for(int i = 0; i < count; ++i)
    {
        if(sem_post(reinterpret_cast< sem_t* >(m_data.ptr)) != 0)
        {
            motor_error_format(Log::thread(), "Could not release semaphore: {0}", strerror(errno));
        }
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    int result;
    while((result = sem_wait(reinterpret_cast< sem_t* >(m_data.ptr))) == -1 && errno == EINTR)
        continue;
    if(result == 0)
    {
        return Finished;
    }
    else
    {
        motor_info_format(Log::thread(), "Semaphore error: {0}", strerror(errno));
        motor_notreached();
        return Abandoned;
    }
}

u32 Semaphore::flushPauseCount()
{
    return 0;
}

}  // namespace Motor

#endif
