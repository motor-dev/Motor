/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/mutex.hh>

#include <pthread.h>

namespace Motor {

Mutex::Mutex() : m_data(new pthread_mutex_t)
{
    pthread_mutex_init(reinterpret_cast< pthread_mutex_t* >(m_data), nullptr);
}

Mutex::~Mutex() noexcept
{
    pthread_mutex_destroy(reinterpret_cast< pthread_mutex_t* >(m_data));
    delete reinterpret_cast< pthread_mutex_t* >(m_data);
}

void Mutex::release()
{
    pthread_mutex_unlock(reinterpret_cast< pthread_mutex_t* >(m_data));
}

Threads::Waitable::WaitResult Mutex::wait()
{
    pthread_mutex_lock(reinterpret_cast< pthread_mutex_t* >(m_data));
    return Finished;
}

}  // namespace Motor
