/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/event.hh>

#include <pthread.h>

namespace Motor {

Event::Event() : m_data(new pthread_cond_t), m_lock(new pthread_mutex_t)
{
    pthread_cond_init(reinterpret_cast< pthread_cond_t* >(m_data), nullptr);
    pthread_mutex_init(reinterpret_cast< pthread_mutex_t* >(m_lock), nullptr);
}

Event::~Event() noexcept
{
    pthread_mutex_destroy(reinterpret_cast< pthread_mutex_t* >(m_lock));
    pthread_cond_destroy(reinterpret_cast< pthread_cond_t* >(m_data));
    delete reinterpret_cast< pthread_mutex_t* >(m_lock);
    delete reinterpret_cast< pthread_cond_t* >(m_data);
}

void Event::set()
{
    pthread_cond_signal(reinterpret_cast< pthread_cond_t* >(m_data));
}

void Event::pulse()
{
    pthread_cond_broadcast(reinterpret_cast< pthread_cond_t* >(m_data));
}

void Event::lock()
{
    pthread_mutex_lock(reinterpret_cast< pthread_mutex_t* >(m_lock));
}

void Event::unlock()
{
    pthread_mutex_unlock(reinterpret_cast< pthread_mutex_t* >(m_lock));
}

Threads::Waitable::WaitResult Event::wait()
{
    int result = pthread_cond_wait(reinterpret_cast< pthread_cond_t* >(m_data),
                                   reinterpret_cast< pthread_mutex_t* >(m_lock));
    if(result == 0)
    {
        return Finished;
    }
    else
    {
        motor_notreached();
        return Abandoned;
    }
}

}  // namespace Motor
