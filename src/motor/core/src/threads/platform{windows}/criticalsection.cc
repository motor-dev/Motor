/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/threads/criticalsection.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {

CriticalSection::CriticalSection() : m_data(new CRITICAL_SECTION)
{
    auto* s = (CRITICAL_SECTION*)m_data;
    InitializeCriticalSection(s);
}

CriticalSection::~CriticalSection()
{
    DeleteCriticalSection((CRITICAL_SECTION*)m_data);
    delete(CRITICAL_SECTION*)m_data;
}

void CriticalSection::enter() const
{
    EnterCriticalSection((CRITICAL_SECTION*)m_data);
}

void CriticalSection::leave() const
{
    LeaveCriticalSection((CRITICAL_SECTION*)m_data);
}

}  // namespace Motor
