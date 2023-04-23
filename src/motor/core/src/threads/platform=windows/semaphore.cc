/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {

#if 0

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.ptr = CreateSemaphore(nullptr, initialCount, 65535, nullptr);
}

Semaphore::~Semaphore()
{
    CloseHandle((HANDLE)m_data.ptr);
}

void Semaphore::release(int count)
{
    ReleaseSemaphore((HANDLE)m_data.ptr, count, nullptr);
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    DWORD rcode = WaitForSingleObject((HANDLE)m_data.ptr, INFINITE);
    switch(rcode)
    {
    case WAIT_OBJECT_0: return Finished;
    case WAIT_FAILED: motor_notreached(); return Abandoned;
    case WAIT_ABANDONED:
    default: return Abandoned;
    }
}

u32 Semaphore::flushPauseCount()
{
    return 0;
}

#else

static i_u32 s_pauseCount;

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.value.set(initialCount);
}

Semaphore::~Semaphore()
{
    WakeByAddressAll(&m_data.value);
}

void Semaphore::release(int count)
{
    m_data.value += count;
    if(count == 1)
    {
        WakeByAddressSingle(&m_data.value);
    }
    else
    {
        WakeByAddressAll(&m_data.value);
    }
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    do
    {
        i32 count = m_data.value--;
        if(count >= 1)
        {
            return Waitable::Finished;
        }
        ++m_data.value;
        ++s_pauseCount;
        WaitOnAddress(&m_data.value, &count, sizeof(m_data.value), INFINITE);
    } while(true);
}

u32 Semaphore::flushPauseCount()
{
    return s_pauseCount.exchange(0);
}

#endif

}  // namespace Motor
