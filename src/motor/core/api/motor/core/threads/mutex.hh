/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_THREADS_MUTEX_HH_
#define MOTOR_CORE_THREADS_MUTEX_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/core/threads/waitable.hh>

namespace Motor {

class ScopedMutexLock;

class motor_api(CORE) Mutex : public Threads::Waitable
{
    friend class ScopedMutexLock;

private:
    void* m_data;

public:
    Mutex();
    ~Mutex();

private:
    void                         release();
    virtual Waitable::WaitResult wait() override;
};

class ScopedMutexLock
{
    MOTOR_NOCOPY(ScopedMutexLock);

private:
    Mutex& m_mutex;

public:
    inline ScopedMutexLock(Mutex& m) : m_mutex(m)
    {
        m_mutex.wait();
    }
    inline ~ScopedMutexLock()
    {
        m_mutex.release();
    }
};

}  // namespace Motor

/**************************************************************************************************/
#endif
