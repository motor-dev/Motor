/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/threads/mutex.hh>

#include <cstdio>
#include <windows.h>

namespace Motor {

static Application* s_application;

static BOOL WINAPI HandleControlEvent(DWORD eventType)
{
    switch(eventType)
    {
    case CTRL_C_EVENT:
    case CTRL_BREAK_EVENT:
        motor_info(Log::system(), "interrupt event");
        if(s_application) s_application->finish();
        return TRUE;
    default: return FALSE;
    }
}

void Application::registerInterruptions()
{
    s_application = this;
    if(GetConsoleWindow())
    {
        SetConsoleCtrlHandler(&HandleControlEvent, TRUE);
    }
}

void Application::unregisterInterruptions()
{
    if(GetConsoleWindow())
    {
        SetConsoleCtrlHandler(&HandleControlEvent, FALSE);
    }
    s_application = nullptr;
}

}  // namespace Motor
