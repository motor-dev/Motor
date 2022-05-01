/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

namespace Motor {

#if 0

Semaphore::Semaphore(int initialCount) : m_data()
{
    m_data.ptr = CreateSemaphore(NULL, initialCount, 65535, NULL);
}

Semaphore::~Semaphore()
{
    CloseHandle((HANDLE)m_data.ptr);
}

void Semaphore::release(int count)
{
    ReleaseSemaphore((HANDLE)m_data.ptr, count, NULL);
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

#else

Semaphore::Semaphore(int initialCount) : m_data()
{
    *reinterpret_cast< i_i32* >(&m_data.value) = initialCount;
}

Semaphore::~Semaphore()
{
    WakeByAddressAll(&m_data.value);
}

void Semaphore::release(int count)
{
    *reinterpret_cast< i_i32* >(&m_data.value) += count;
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
    i_i32& value = *reinterpret_cast< i_i32* >(&m_data.value);
    do
    {
        i32 count = value--;
        if(count >= 1)
        {
            return Waitable::Finished;
        }
        ++value;
        WaitOnAddress(&m_data.value, &count, sizeof(i_u32), INFINITE);
    } while(1);
}

#endif

}  // namespace Motor
