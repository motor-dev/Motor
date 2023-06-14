/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <errno.h>
#include <stdio.h>

#include <limits.h>
#include <linux/futex.h>
#include <sys/syscall.h>
#include <unistd.h>

namespace Motor {

static i_u32 s_pauseCount;

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.value.set(initialCount);
}

Semaphore::~Semaphore()
{
    syscall(__NR_futex, &m_data.value, FUTEX_WAKE, INT_MAX);
}

void Semaphore::release(int count)
{
    m_data.value += count;
    if(syscall(__NR_futex, &m_data.value, FUTEX_WAKE, count) < 0)
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
        result = syscall(__NR_futex, &m_data.value, FUTEX_WAIT, count, NULL);
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
