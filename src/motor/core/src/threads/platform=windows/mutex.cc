/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/mutex.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {

Mutex::Mutex() : m_data(CreateMutex(nullptr, FALSE, nullptr))
{
}

Mutex::~Mutex()
{
    CloseHandle((HANDLE)m_data);
}

void Mutex::release()
{
    ReleaseMutex((HANDLE)m_data);
}

Threads::Waitable::WaitResult Mutex::wait()
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
