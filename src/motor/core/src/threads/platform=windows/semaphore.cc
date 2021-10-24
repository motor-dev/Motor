/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/semaphore.hh>

namespace Motor {

Semaphore::Semaphore(int initialCount) : m_data(CreateSemaphore(NULL, initialCount, 65535, NULL))
{
}

Semaphore::~Semaphore()
{
    CloseHandle((HANDLE)m_data);
}

void Semaphore::release(int count)
{
    ReleaseSemaphore((HANDLE)m_data, count, NULL);
}

Threads::Waitable::WaitResult Semaphore::wait()
{
    DWORD rcode = WaitForSingleObject((HANDLE)m_data, INFINITE);
    switch(rcode)
    {
    case WAIT_OBJECT_0: return Finished;
    case WAIT_FAILED: motor_notreached(); return Abandoned;
    case WAIT_ABANDONED:
    default: return Abandoned;
    }
}

}  // namespace Motor