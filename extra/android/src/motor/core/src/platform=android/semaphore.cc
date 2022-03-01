/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <cerrno>
#include <stdio.h>

#include <limits.h>
#include <linux/futex.h>
#include <sys/syscall.h>
#include <unistd.h>

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data()
{
    *reinterpret_cast< i_i32* >(&m_data.value) = initialCount;
}

Semaphore::~Semaphore()
{
    syscall(__NR_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAKE, INT_MAX);
}

void Semaphore::release(int count)
{
    *reinterpret_cast< i_i32* >(&m_data.value) += count;
    if(syscall(__NR_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAKE, count) < 0)
    {
        motor_error("Semaphore error: %d[%s]" | errno | strerror(errno));
        motor_notreached();
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    int    result;
    i_i32* value = reinterpret_cast< i_i32* >(&m_data.value);
    do
    {
        i32 count = *value += 0;
        if(count > 0)
        {
            if(value->setConditional(count - 1, count) == count) return Waitable::Finished;
        }

        result = syscall(__NR_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAIT, count,
                         NULL);
    } while(result == 0 || errno == EAGAIN);

    motor_error("Semaphore error: %d-%d[%s]" | result | errno | strerror(errno));
    motor_notreached();
    return Abandoned;
}

}  // namespace Motor
