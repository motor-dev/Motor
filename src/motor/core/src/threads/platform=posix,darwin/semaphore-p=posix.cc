/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <cerrno>
#include <stdio.h>

#ifdef __linux

#    include <limits.h>
#    include <linux/futex.h>
#    include <sys/syscall.h>
#    include <unistd.h>

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data()
{
    *reinterpret_cast< i_i32* >(&m_data.value) = initialCount;
}

Semaphore::~Semaphore()
{
    syscall(SYS_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAKE_PRIVATE, INT_MAX);
}

void Semaphore::release(int count)
{
    *reinterpret_cast< i_i32* >(&m_data.value) += count;
    if(syscall(SYS_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAKE_PRIVATE, count) < 0)
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

        result = syscall(SYS_futex, reinterpret_cast< i_i32* >(&m_data.value), FUTEX_WAIT_PRIVATE,
                         count, NULL);
    } while(result == 0 || errno == EAGAIN);

    motor_error("Semaphore error: %d-%d[%s]" | result | errno | strerror(errno));
    motor_notreached();
    return Abandoned;
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
        motor_error("Could not initialize semaphore: %s" | strerror(errno));
    }
}

Semaphore::~Semaphore()
{
    if(sem_destroy(reinterpret_cast< sem_t* >(m_data.ptr)) != 0)
    {
        motor_error("Could not initialize semaphore: %s" | strerror(errno));
    }
    delete reinterpret_cast< sem_t* >(m_data.ptr);
}

void Semaphore::release(int count)
{
    for(int i = 0; i < count; ++i)
    {
        if(sem_post(reinterpret_cast< sem_t* >(m_data.ptr)) != 0)
        {
            motor_error("Could not release semaphore: %s" | strerror(errno));
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
        motor_info("Semaphore error: %s" | strerror(errno));
        motor_notreached();
        return Abandoned;
    }
}

}  // namespace Motor

#endif
