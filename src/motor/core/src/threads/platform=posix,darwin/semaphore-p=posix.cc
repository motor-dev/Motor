/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#include <motor/core/timer.hh>

#include <cerrno>
#include <semaphore.h>
#include <stdio.h>

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data(new sem_t)
{
    if(sem_init(reinterpret_cast< sem_t* >(m_data), 0, initialCount) != 0)
    {
        motor_error("Could not initialize semaphore: %s" | strerror(errno));
    }
}

Semaphore::~Semaphore()
{
    if(sem_destroy(reinterpret_cast< sem_t* >(m_data)) != 0)
    {
        motor_error("Could not initialize semaphore: %s" | strerror(errno));
    }
    delete reinterpret_cast< sem_t* >(m_data);
}

void Semaphore::release(int count)
{
    for(int i = 0; i < count; ++i)
    {
        if(sem_post(reinterpret_cast< sem_t* >(m_data)) != 0)
        {
            motor_error("Could not release semaphore: %s" | strerror(errno));
        }
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    int result;
    while((result = sem_wait(reinterpret_cast< sem_t* >(m_data))) == -1 && errno == EINTR)
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
