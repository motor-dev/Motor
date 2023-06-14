/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_THREADS_MUTEX_HH
#define MOTOR_CORE_THREADS_MUTEX_HH

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
    ~Mutex() override;

private:
    void                 release();
    Waitable::WaitResult wait() override;
};

class ScopedMutexLock
{
private:
    Mutex& m_mutex;

public:
    inline explicit ScopedMutexLock(Mutex& m) : m_mutex(m)
    {
        m_mutex.wait();
    }
    inline ~ScopedMutexLock()
    {
        m_mutex.release();
    }

    ScopedMutexLock(const ScopedMutexLock&)            = delete;
    ScopedMutexLock& operator=(const ScopedMutexLock&) = delete;
    ScopedMutexLock(ScopedMutexLock&&)                 = delete;
    ScopedMutexLock& operator=(ScopedMutexLock&&)      = delete;
};

}  // namespace Motor

#endif
